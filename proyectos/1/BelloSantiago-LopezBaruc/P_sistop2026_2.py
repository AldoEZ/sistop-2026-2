import os
import struct
import threading
from datetime import datetime

## COMMIT 1.
## -Creación de las dos clases principales del programa. Sistema de archivos: FiUnamFs, Archivo: File
## -Creación de los métodos para la obtención para el mapeo de directorios. Checando solamente los archivos denotados por "-" poara denotar que la entrada no esta vacia. 
##  Adjuntando los metadatos de los archivos existente a una lista de archivos, atributo de la clase FiUnamFs.
## -Creación del método de carga para el sistema de archivos. Cargando solamente archivos válidos mediante la cadena 'FiUnamFs24-2'
## -Creación de dos métodos, el primero para la obtención del contenido de los archivos perse. Donde el segundo de manera complementaria hara uso de este primero para la inserción
##  al sistema de computo del usuario.
## -Esta primera implementación no hace uso de hilos. Sin embargo se esta planificando para que la implementación sea sencilla. Es solamente para tener la lógica fundamental primero.

class File:
    """
    Clase que representa un archivo individual dentro del sistema FiUnamFS.
    Almacena los metadatos extraídos de la entrada del directorio y permite acceder a su contenido.
    """
    def __init__(self, name: str, size: int, initial_cluster: int, creation_date: str, update_date: str, dir_path: str ) -> None:
        self.tam_cluster = 2048  # Tamaño de clúster estático por defecto
        self.name = name
        self.size= size
        self.initial_cluster = initial_cluster
        self.creation_date = self._fecha_formato(creation_date) 
        self.update_date = self._fecha_formato(update_date) 
        self.dir_path = dir_path  # Ruta a la imagen del sistema de archivos (.img)

    def _fecha_formato(self, date:str) -> str:
        """
        Toma la cadena de fecha cruda (AAAAMMDDHHMMSS) y la formatea
        a una versión más legible (AAAA-MM-DD HH:MM:SS).
        """
        year = date[:4]
        month = date[4:6]
        day = date[6:8]
        hour = date[8:10]
        minute = date[10:12]
        second = date[12:14]

        new_date = f"{year}-{month}-{day} {hour}:{minute}:{second}"
        return new_date
    
    def obtener_contenido(self):
        """
        Abre el archivo de imagen del sistema, se posiciona en el clúster
        inicial correspondiente a este archivo y lee su tamaño exacto en bytes.
        """
        # Se calcula el byte exacto donde inicia el archivo
        posicion_inicial = self.initial_cluster * self.tam_cluster

        with open(self.dir_path, 'rb') as file:
            file.seek(posicion_inicial)
            return file.read(self.size) # Se lee únicamente el tamaño del archivo, no todo el clúster


    def mostrar_informacion(self) -> None:
        """Imprime los metadatos del archivo en consola."""
        print("=== INFORMACIÓN DEL ARCHIVO ===")
        print(f"Nombre:           {self.name}")
        print(f"Tamaño:           {self.size} bytes")
        print(f"Cluster Inicial:  {self.initial_cluster}")
        print(f"Fecha Creación:   {self.creation_date}")
        print(f"Fecha Modificación: {self.update_date}")
        print(f"Ruta Directorio:  {self.dir_path}")
        print("===============================")
    
class FiUnamFS:
    """
    Clase principal que gestiona el sistema de archivos FiUnamFS.
    Se encarga de montar la imagen, validar su estructura y mapear los archivos internos.
    """
    def __init__(self, path: str):
        self.path = path
        self.etiqueta = ""
        self.tam_cluster = 0
        self.clusters_dir = 0
        self.clusters_unity = 0
        self.archivos_validos = {}  # Diccionario: {nombre_archivo: cluster_inicial}
        self.lista_archivos = []    # Lista de objetos File
       
        # Al instanciar, se intenta montar (validar) el sistema. Si falla, lanza excepción.
        if not self.upload():
            raise Exception("No se pudo montar el sistema de archivos: Falló la validación.")
        

    def mapear_directorio(self):
        """
        Escanea la sección del directorio dentro de la imagen del sistema de archivos,
        leyendo entradas de 64 bytes para extraer los archivos válidos y crear objetos File.
        """
        self.archivos_validos = {} 
        self.lista_archivos = [] 
        # El directorio empieza después del Superbloque (que asume toma 1 clúster)
        offset_dir = 1 * self.tam_cluster
            
        print("\n--- ESCANEANDO DIRECTORIO ---")
        with open(self.path, 'rb') as file:
            file.seek(offset_dir)
                
            # Calcula cuántas entradas caben en los clústers asignados al directorio (64 bytes por entrada)
            total_entradas = self.clusters_dir * (self.tam_cluster // 64)
                
            for _ in range(total_entradas):
                entrada = file.read(64)
                if not entrada: break  # Fin del archivo prematuro
                    
                # El primer byte (45 en ASCII es '-') indica que la entrada está en uso
                if entrada[0] == 45: 
                    
                    # Extraer el nombre (15 bytes), cortando en el primer byte nulo y decodificando
                    nombre_bytes = entrada[1:16].split(b'\x00')[0] 
                    nombre = nombre_bytes.decode('ascii').strip('#').strip()
                        
                    # Extraer metadatos usando struct (Little Endian, Unsigned Int)
                    size = struct.unpack('<I', entrada[16:20])[0]
                    cluster_ini = struct.unpack('<I', entrada[20:24])[0]
                    
                    # Extraer fechas y limpiar caracteres nulos
                    c_date = entrada[30:44].decode('ascii').strip('\x00').strip()
                    u_date = entrada[50:64].decode('ascii').strip('\x00').strip()

                    self.archivos_validos[nombre] = cluster_ini

                    # Instanciar el objeto File con los datos obtenidos
                    nuevo_archivo = File(
                        name=nombre, 
                        size=size, 
                        initial_cluster=cluster_ini, 
                        creation_date=c_date, 
                        update_date=u_date, 
                        dir_path=self.path
                    )
                    self.lista_archivos.append(nuevo_archivo)
                        
                    print(f"Archivo: {nombre:<15} | Cluster Inicial: {cluster_ini}")

            print(f"-----------------------------\nDirectorio mapeado: {len(self.archivos_validos)} archivos encontrados.\n")


    def copia_TO_MyPC(self, path:str , file: File ) -> bool: # El path debe de ser la dirección hacia donde se busca insertar el archivo.
        """
        Extrae un archivo del sistema FiUnamFS y lo guarda en el sistema de archivos local del usuario.
        """
        a = self.lista_archivos[2] # Variable actualmente no utilizada

        # Evita sobrescribir si el archivo ya existe en la ruta destino
        if not os.path.exists(path + f'/{file.name}'):
            content = file.obtener_contenido()

            try:
                # Escribe los bytes extraídos en un nuevo archivo en la PC
                with open(path + f'/{file.name}', 'wb') as new_file:
                    new_file.write(content)
                return True
            except:
                return False
    
    def upload(self) -> bool:
        """
        Valida el superbloque del sistema de archivos comprobando firmas, versión y extrayendo 
        la configuración básica (tamaño de clúster, número de clústers, etc.).
        """
        try:
            with open(self.path, 'rb') as file:
                # Capa 1: Validación de bytes nulos iniciales (0 a 3)
                file.seek(0)
                if file.read(4) != b'\x00\x00\x00\x00':
                    print('Archivo no válido. CAPA 1')
                    return False
                print('Capa 1 EXITOSA')

                # Capa 2: Validación del nombre del sistema "FiUnamFS" (bytes 5 a 12)
                file.seek(5)
                f13 = file.read(8)
                if f13.decode('ascii') != 'FiUnamFS':
                    print('Sistema no válido. CAPA 2')
                    return False
                print("Capa 2 EXITOSA_Sistema válido")

                # Capa 3: Validación de la versión "24-2" (bytes 14 a 17)
                file.seek(14)
                f18 = file.read(4)
                version_leida = f18.decode('ascii')
                if version_leida != '24-2': 
                    print(f'Version incompatible ({version_leida}). CAPA 3')
                    return False
                print("Capa 3 EXITOSA_Version compatible")

                # Extracción de metadatos del Superbloque
                file.seek(20)
                self.etiqueta = file.read(15).decode('ascii').strip()

                file.seek(40)
                self.tam_cluster = struct.unpack('<I', file.read(4))[0]

                file.seek(50)
                self.clusters_dir = struct.unpack('<I', file.read(4))[0]

                file.seek(60)
                self.clusters_unity = struct.unpack('<I', file.read(4))[0]

                return True

        except FileNotFoundError:
            print(f"Error: El archivo {self.path} no existe.")
            return False
        except Exception as e:
            print(f"Error inesperado: {e}")
            return False


    def __str__(self):
        """Representación en texto de los metadatos principales del volumen."""
        return (f"--- FiUnamFS Info ---\n"
                f"Etiqueta: {self.etiqueta}\n"
                f"Tamaño Clúster: {self.tam_cluster} bytes\n"
                f"Clústers Directorio: {self.clusters_dir}\n"
                f"Clústers Totales: {self.clusters_unity}\n"
                f"---------------------")


# ==========================================
# BLOQUE DE PRUEBAS DEL SCRIPT
# ==========================================
ruta_disco = '/Users/santiagobello/Downloads/fiunamfs.img'

try:
    disco = FiUnamFS(ruta_disco)
    print(disco)
    
    disco.mapear_directorio()

    print(disco.archivos_validos['mensaje.jpg'])
    
    print(disco.copia_TO_MyPC('/Users/santiagobello/Downloads/'))

except Exception as e:
    print(f"Hubo un error al leer el sistema de archivos: {e}")