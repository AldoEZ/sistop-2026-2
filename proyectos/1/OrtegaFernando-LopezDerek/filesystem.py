import struct
import threading

CLUSTER_SIZE = 2048
DIRECTORY_START = 2048
ENTRY_SIZE = 64
TOTAL_ENTRIES = 256

class FiUnamFS:
    def __init__(self, ruta):
        self.ruta = ruta
        self.lock = threading.Lock()

    def validar_fs(self):
        """ Valida que el sistema de archivos sea 
        FiUnamFS versión 26-2.
        """
        with open(self.ruta, 'rb') as archivo:

            archivo.seek(5)
            nombre = archivo.read(8).decode('ascii')

            archivo.seek(14)
            version = archivo.read(4).decode('ascii')

            print('Sistema:', nombre)
            print('Version:', version)

            if nombre != 'FiUnamFS':
                return False

            if version != '26-2':
                return False

        return True

    def listar_directorio(self):
        """
        Lista los archivos en el directorio raíz de FiUnamFS.
        Devuelve una lista de diccionarios con información de cada archivo.
        """
        archivos_encontrados = []

        with self.lock:

            with open(self.ruta, 'rb') as archivo:

                for i in range(TOTAL_ENTRIES):

                    offset = DIRECTORY_START + (i * ENTRY_SIZE)

                    archivo.seek(offset)
                    entrada = archivo.read(ENTRY_SIZE)

                    tipo = entrada[0:1].decode('ascii')

                    nombre = entrada[1:16].decode('ascii')
                    nombre = nombre.replace('\x00', '').strip()

                    if tipo == '-':

                        tamano = struct.unpack('<I', entrada[16:20])[0]
                        cluster_inicial = struct.unpack('<I', entrada[20:24])[0]

                        archivos_encontrados.append({
                            'nombre': nombre,
                            'tamano': tamano,
                            'cluster': cluster_inicial
                        })

        return archivos_encontrados

    def mostrar_archivos(self):
        """
        Muestra la información de los archivos encontrados 
        en el directorio raíz.
        """
        archivos = self.listar_directorio()

        print('\nContenido de FiUnamFS:\n')

        for archivo in archivos:
            print(f"Nombre: {archivo['nombre']}")
            print(f"Tamano: {archivo['tamano']} bytes")
            print(f"Cluster inicial: {archivo['cluster']}")
            print('--------------------------')

    def copiar_desde_fs(self, nombre_archivo, destino):
        """
        Copia un archivo desde FiUnamFS hacia
        el destino especificado en el sistema host.
        """
        with self.lock:
            with open(self.ruta, 'rb') as archivo:
                for i in range(TOTAL_ENTRIES):
                    offset = DIRECTORY_START + (i * ENTRY_SIZE)
                    archivo.seek(offset)
                    entrada = archivo.read(ENTRY_SIZE)
                    tipo = entrada[0:1].decode('ascii')
                    nombre = entrada[1:16].decode('ascii')
                    nombre = nombre.replace('\x00', '').strip()

                    if tipo == '-' and nombre == nombre_archivo:
                        tamano = struct.unpack('<I', entrada[16:20])[0]
                        cluster = struct.unpack('<I', entrada[20:24])[0]
                        inicio = cluster * CLUSTER_SIZE
                        archivo.seek(inicio)
                        datos = archivo.read(tamano)
                        
                        with open(destino, 'wb') as salida:
                            salida.write(datos)

                        print('Archivo copiado correctamente.')
                        
                        return

        print('Archivo no encontrado.')
