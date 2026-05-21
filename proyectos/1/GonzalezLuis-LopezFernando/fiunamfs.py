"""
Proyecto (Micro) sistema de archivos multihiloss
Autores: 
    - Gonzalez Falcon Luis Adrían
    - Lopez Morales Fernando Samuel
Entrega 2026-05-21
"""
import struct
import os
import math
import datetime

class FiUnamFS:
    
    # TODO Leer del superbloque!!
    # Constantes importantes de los requerimientos
    TAMANO_CLUSTER = 2048
    TAMANO_ENTRADA_DIR = 64
    CLUSTERS_DIRECTORIO = 8
    # Ver documentación para enteder de donde salen los valores

    #Formato como printf en C, o el formateo en print(f'')
    FORMATO_ENTRADA = "<c15sII6x14s6x14s"
    # Ver documentación para entender el valor y razon de cada símbolo

    def __init__(self, ruta_imagen):
        # prueba primer imagen
        self.ruta_imagen = ruta_imagen
        self.archivo = None
        self.lock = None

    def _obtener_mapa_clusters(self):
        """
        Recorre el directorio y crea una lista booleana representando los 720 clusters para ver cuales están disponibles
        true = ocupado, false = libre
        Devuelve adeḿas la posición (en bytes) de la primera entrada libre en el directorio
        """

        # Inicializamos los 720 clusters como libres (False)
        TOTAL_CLUSTERS = 720 # #TODO Cambiar!
        mapa_clusters = [False] * TOTAL_CLUSTERS
        
        # El Superbloque (Cluster 0) y el Directorio (1 al 8) se marcan ocupados
        for i in range(9):
            mapa_clusters[i] = True
            
        inicio_directorio = self.TAMANO_CLUSTER * 1
        total_entradas = (self.CLUSTERS_DIRECTORIO * self.TAMANO_CLUSTER) // self.TAMANO_ENTRADA_DIR
        
        posicion_entrada_libre = -1
        self.archivo.seek(inicio_directorio)
        
        for i in range(total_entradas):
            posicion_actual = inicio_directorio + (i * self.TAMANO_ENTRADA_DIR)
            self.archivo.seek(posicion_actual)
            entrada_bytes = self.archivo.read(self.TAMANO_ENTRADA_DIR)
            
            if len(entrada_bytes) < self.TAMANO_ENTRADA_DIR:
                break
                
            datos = struct.unpack(self.FORMATO_ENTRADA, entrada_bytes)
            #print(f"Queeee: {datos}")
            tipo_archivo = datos[0].decode('ascii', errors='ignore')
            
            if tipo_archivo == '-':
                # El archivo existe, calculamos qué clusters ocupa para marcarlos
                tamano = datos[2]
                cluster_inicial = datos[3]
                clusters_ocupados = math.ceil(tamano / self.TAMANO_CLUSTER)  #debe ser mayor para caber sin problemas
                
                for c in range(cluster_inicial, cluster_inicial + clusters_ocupados):
                    if c < TOTAL_CLUSTERS:
                        mapa_clusters[c] = True
                        
            elif tipo_archivo == '/' and posicion_entrada_libre == -1:
                # Guardamos la ubicación de la primera entrada vacía que veamos
                posicion_entrada_libre = posicion_actual
                
        return mapa_clusters, posicion_entrada_libre

    def _buscar_espacio_contiguo(self, mapa_clusters, clusters_necesarios):
        """
        Busca secuencialmente en el mapa de clusters un espacio con suficientes 
        clusters libres (marcados en false) consecutivos. Retorna el cluster inicial o -1 si no hay espacio
        """
        contador_consecutivos = 0
        cluster_inicio_candidato = -1
        
        # Se empieza a buscar desde el CLuster 9 (Zona de datos)
        for i in range(9, len(mapa_clusters)):
            if not mapa_clusters[i]: # Si está disponible
                if contador_consecutivos == 0:
                    cluster_inicio_candidato = i
                contador_consecutivos += 1
                
                if contador_consecutivos == clusters_necesarios:
                    return cluster_inicio_candidato
            else:
                # No se cumple el número de clusters consecutivos, por lo que continuamos a la siguiente iteración
                contador_consecutivos = 0
                cluster_inicio_candidato = -1
                
        return -1 # No se encontró espacio suficiente

    # por ahora hace la conexión a la imagen (#CAMBIAR)
    def conectar(self):

       # Verifica si el archivo existe en la ruta indicada
        if not os.path.exists(self.ruta_imagen):
            raise FileNotFoundError(f"El archivo de imagen '{self.ruta_imagen}' no existe en esta ruta.")
        
        self.archivo = open(self.ruta_imagen, 'r+b')
        print(f"[+] Conectado exitosamente a la imagen: {self.ruta_imagen}")


    def validar_superbloque(self):
        if not self.archivo:
            raise ConnectionError("No hay un archivo abierto") # se teine que llamar primero a conectar()
            
        self.archivo.seek(0)
        superbloque = self.archivo.read(64)
        
        # Extracción de bytes :ooo
        
        #identificacion = superbloque[5:14]
        identificacion = superbloque[5:14].strip(b'\x00')
        # version = superbloque[14:19]
        version = superbloque[14:19].strip(b'\x00')
        # se quita debe quitar el nulo?
        
        print(f"Verificando info del SUperbloque: Iden: {identificacion}, v.: {version}")
        
        if identificacion != b'FiUnamFS':
            self.desconectar()
            raise ValueError(f"Error: {identificacion} no es el disco correcto :(")
            
        # Se aceptara '24-2' (la que tiene el profe) o '26-2' (como debe ser)
        if version not in (b'24-2', b'26-2'):
            self.desconectar()
            raise ValueError(f"Error: Versión {version} no soportada :(")
            
        print("OK")
        return True

    """
    1: Listar los contenidos del directorio
    """
    def listar_directorio(self):
        # IMPLEMENTAR DIRECTAMENTE EN FUSE

        if not self.archivo:
            raise ConnectionError("No hay un archivo abierto")

        #print("\n------- Contenido:")
        print(f"{'Nombre':<15} | {'Tamaño (Bytes)':<14} | {'Cluster Inicial':<15} | {'Fecha Creación'}")
        print("-----------------------------------------------------")

        #El directorio empieza en el byte 2048: CLuster 1
        inicio_directorio = self.TAMANO_CLUSTER * 1
        self.archivo.seek(inicio_directorio)

        # Calcula el total de entradas posibles (256)
        total_entradas = (self.CLUSTERS_DIRECTORIO * self.TAMANO_CLUSTER) // self.TAMANO_ENTRADA_DIR
        archivos_encontrados = 0

        for _ in range(total_entradas):
            entrada_bytes = self.archivo.read(self.TAMANO_ENTRADA_DIR)
            
            #Por seguridad, si leemos menos de 64 bytes salimos del bucle
            if len(entrada_bytes) < self.TAMANO_ENTRADA_DIR:
                break

            #USANDO FORMATO DECLARADO EN CONSTANTES IMPORTANTES
            datos = struct.unpack(self.FORMATO_ENTRADA, entrada_bytes)
            
            #Extraemos primer byte: tipo de archivo
            tipo_archivo = datos[0].decode('ascii', errors='ignore')

            # '-': con contenido, '/': vacío
            if tipo_archivo == '-':
            
                #nombre = datos[1].decode('ascii', errors='ignore') #decodifca correctamente
                #nombre = nombre.strip('\x00 ') # se quita nulo
                #nombre = nombre.replace('#', '') # se reemplazan los # extra
                nombre = datos[1].decode('ascii', errors='ignore').strip('\x00 ').replace('#', '')
                tamano = datos[2]
                cluster_inicial = datos[3]
                
                # fecha de creación
                fecha_creacion = datos[4].decode('ascii', errors='ignore').strip('\x00 ') # Se quitan los nulos

                # Imprimimos la fila con formato alineado
                print(f"{nombre:<15} | {tamano:<14} | {cluster_inicial:<15} | {fecha_creacion}")
                archivos_encontrados += 1

        if archivos_encontrados == 0:
            print("El directorio está vacio")
        print("-----")
        print(f"Total de archivos con contenido: {archivos_encontrados}\n")



    def copiar_al_exterior(self, nombre_fiunamfs, ruta_destino_local):
        """
        2: Copia un archivo desde FiUnamFS hacia local
        """
        if not self.archivo:
            raise ConnectionError("No hay un archivo abierto")

        # Buscar el archivo en el directorio
        inicio_directorio = self.TAMANO_CLUSTER * 1
        self.archivo.seek(inicio_directorio)
        total_entradas = (self.CLUSTERS_DIRECTORIO * self.TAMANO_CLUSTER) // self.TAMANO_ENTRADA_DIR
        
        encontrado = False
        tamano_archivo = 0
        cluster_inicial = 0

        for _ in range(total_entradas):
            entrada_bytes = self.archivo.read(self.TAMANO_ENTRADA_DIR)
            if len(entrada_bytes) < self.TAMANO_ENTRADA_DIR:
                break

            datos = struct.unpack(self.FORMATO_ENTRADA, entrada_bytes)
            tipo_archivo = datos[0].decode('ascii', errors='ignore')

            if tipo_archivo == '-':
                nombre_actual = datos[1].decode('ascii', errors='ignore').strip('\x00 ').replace('#', '')
                
                # Linealmente recorremos, lo encontramos y rompemos bucle guardando datos
                if nombre_actual == nombre_fiunamfs:
                    tamano_archivo = datos[2]
                    cluster_inicial = datos[3]
                    encontrado = True
                    break

        if not encontrado:
            print(f"Error: El archivo '{nombre_fiunamfs}' no existe dentro de FiUnamFS")
            return False

        # Extrae los datos y los escribirlos en local
        byte_inicio = cluster_inicial * self.TAMANO_CLUSTER
        self.archivo.seek(byte_inicio)
        
        # Lee los bytes exactos que mide el archivo
        datos_archivo = self.archivo.read(tamano_archivo)

        # Escribe los bytes en un nuevo archivo en local
        try:
            with open(ruta_destino_local, 'wb') as f_destino:
                f_destino.write(datos_archivo)
            print(f"Archivo: '{nombre_fiunamfs}' copiado con exito como '{ruta_destino_local}'")
            return True
        except IOError as e:
            print(f"Error al guardar el archivo en local: {e}")
            return False
    
    def copiar_al_interior(self, ruta_origen_local, nombre_fiunamfs):
        """
        3. Copiar un archivo de local a FIUnamFS
        """
        if not self.archivo:
            raise ConnectionError("No hay un archivo abierto.")

        if not os.path.exists(ruta_origen_local):
            print(f"Error: El archivo local '{ruta_origen_local}' no existe")
            return False

        # Medir el archivo y calcular lo que se necesita
        tamano_archivo = os.path.getsize(ruta_origen_local)
        clusters_necesarios = math.ceil(tamano_archivo / self.TAMANO_CLUSTER) # Es importante ceil() para que de 'un cluster más' si es que no es exacto
        
        # Obtener mapa de la memoria (clusters)
        mapa_clusters, posicion_entrada_libre = self._obtener_mapa_clusters()
        
        if posicion_entrada_libre == -1:
            print("Error: El directorio está lleno\n-- No caben más archivos")
            return False
            
        # Buscar espacio contiguo
        cluster_inicial = self._buscar_espacio_contiguo(mapa_clusters, clusters_necesarios)
        
        if cluster_inicial == -1:
            print("Error: No hay suficiente espacio contiguo en el disco")
            return False
            
        # Escribir los datos en la zona de datos
        byte_inicio_datos = cluster_inicial * self.TAMANO_CLUSTER
        try:
            with open(ruta_origen_local, 'rb') as f_origen:
                datos_a_escribir = f_origen.read()
                
            self.archivo.seek(byte_inicio_datos)
            self.archivo.write(datos_a_escribir)
        except IOError as e:
            print(f"Error al leer el archivo local: {e}")
            return False

        # Actualizar entrada en el directorio
        fecha_actual = datetime.datetime.now().strftime('%Y%m%d%H%M%S').encode('ascii')
        nombre_bytes = nombre_fiunamfs.encode('ascii')
        
        # struct.pack llena con nulos los espacios que sobren en el nombre
        nueva_entrada = struct.pack(
            self.FORMATO_ENTRADA,
            b'-',
            nombre_bytes,
            tamano_archivo,
            cluster_inicial,
            fecha_actual,
            fecha_actual
        )

        self.archivo.seek(posicion_entrada_libre)
        self.archivo.write(nueva_entrada)
        
        print(f"Archivo '{ruta_origen_local}' insertado como '{nombre_fiunamfs}' exitosamente")
        print(f"    -> Ocupa {clusters_necesarios} clusters, empezando en el cluster {cluster_inicial}")
        return True

        """
        Punto 4: Eliminar archivo de la imagen
        """
    def eliminar_archivo(self, nombre_fiunamfs):
        if not self.archivo:
            raise ConnectionError("No hay una archivo abierto")

        inicio_directorio = self.TAMANO_CLUSTER * 1
        total_entradas = (self.CLUSTERS_DIRECTORIO * self.TAMANO_CLUSTER) // self.TAMANO_ENTRADA_DIR
        
        for i in range(total_entradas):
            posicion_entrada = inicio_directorio + (i * self.TAMANO_ENTRADA_DIR)
            self.archivo.seek(posicion_entrada)
            entrada_bytes = self.archivo.read(self.TAMANO_ENTRADA_DIR)
            
            if len(entrada_bytes) < self.TAMANO_ENTRADA_DIR:
                break

            datos = struct.unpack(self.FORMATO_ENTRADA, entrada_bytes)
            tipo_archivo = datos[0].decode('ascii', errors='ignore')

            if tipo_archivo == '-':
                nombre_actual = datos[1].decode('ascii', errors='ignore').strip('\x00 ').replace('#', '')
                
                if nombre_actual == nombre_fiunamfs:
                    # Ubicar el cursor en la posicion del archivo
                    self.archivo.seek(posicion_entrada)
                    
                    #Se sobreescriben los bytes
                    nuevo_tipo = b'/'
                    nuevo_nombre = b'###############'
                    
                    #Se escribe en el disco
                    self.archivo.write(nuevo_tipo + nuevo_nombre)
                    
                    print(f"Eliminando archivo {nombre_fiunamfs}")
                    return True

        print(f"No se encontró el archivo '{nombre_fiunamfs}' a eliminar")
        return False        
        

    def desconectar(self):
        if self.archivo and not self.archivo.closed:
            self.archivo.close()
            print("Archivo de imagen cerrado")


if __name__ == "__main__":
    ruta_prueba = "./fiunamfs.img" 
    
    try:
        fs = FiUnamFS(ruta_prueba)
        fs.conectar()
        fs.validar_superbloque()
        
        print("\n Listar_directorio")
        fs.listar_directorio()

        print("\n Eliminando archivo")
        #fs.eliminar_archivo('script_final.py')

        print("\n Listar_directorio DESPUÉS de borrar:")
        fs.listar_directorio()
        
        #print("\nPruebita copiando imagen pro")
        #fs.copiar_al_exterior("script_final.py", "codigo_extraido.py")

        #print("\n Listar_directorio DESPUÉS de borrar:")
        #fs.listar_directorio()
        
        print("\nPruebita copiando imagen pro")
        fs.copiar_al_exterior("logo.png", "logo_extraido.png")

        print("\n Listar_directorio DESPUÉS")
        fs.listar_directorio()

        # (Después de hacer listar_directorio o de eliminar algo)
        
        print("\n Intentando insertar archivo")
        fs.copiar_al_interior("fiunamfs.py", "script_final.py")
        
        print("\n Listar_directorio DESPUÉS de insertar:")
        fs.listar_directorio()
        
        
        fs.desconectar()
    except Exception as e:
        print(f"Ocurrió un error inesperado :( :\n{e}")