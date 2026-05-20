"""
Proyecto (Micro) sistema de archivos multihiloss
Autores: 
    - Gonzalez Falcon Luis Adrían
    - Lopez Morales Fernando Samuel
ENtrega 2026-05-21
"""
import struct
import os

class FiUnamFS:
    
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
        
        print("\n Listar_directorio ANTES de borrar:")
        fs.listar_directorio()

        print("\n Eliminando 'mensaje.jpg'")
        fs.eliminar_archivo('mensaje.jpg')

        print("\n Listar_directorio DESPUÉS de borrar:")
        fs.listar_directorio()
        
        print("\nPruebita copiando imagen pro")
        fs.copiar_al_exterior("logo.png", "extraido_logo.png")
        
        fs.desconectar()
    except Exception as e:
        print(f"Ocurrió un error inesperado :( :\n{e}")