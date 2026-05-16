import os
import stat
import errno
import struct
import time
from fuse import Operations, LoggingMixIn

class FiUnamFS(LoggingMixIn, Operations):
    """
    Capa Productora: Recibe llamadas del sistema operativo vía FUSE 
    y encola tareas al Worker.
    """
    def __init__(self, worker):
        self.worker = worker
        self.metadata = {}
        
        # caché en memoria para agilizar consultas
        self.directory = {}

        # validación del disco
        self._mount_filesystem()
    
    def _mount_filesystem(self):
        print("Leyendo superbloque...")
        # El superbloque siempre ocupa los primeros 64 bytes (o el Clúster 0 entero)
        sb_data = self.worker.read_bytes(0, 64)
        
        # validación del bloque
        firma = sb_data[5:14].decode('ascii').strip('\x00')
        if firma != 'FiUnamFS':
            raise ValueError(f"Firma del sistema de archivos inválida: '{firma}'")
            
        version = sb_data[14:19].decode('ascii').strip('\x00')
        if version != '26-2':
            raise ValueError(f"Versión de FiUnamFS no soportada: '{version}'")
            
        label = sb_data[20:36].decode('ascii').strip('\x00')

        # LECTURA DE METADATOS MATEMÁTICOS (<I es Entero 32-bits Little Endian)
        cluster_size = struct.unpack('<I', sb_data[40:44])[0]
        dir_clusters = struct.unpack('<I', sb_data[50:54])[0]
        total_clusters = struct.unpack('<I', sb_data[60:64])[0]
        
        self.metadata = {
            'label': label,
            'cluster_size': cluster_size,
            'dir_clusters': dir_clusters,
            'total_clusters': total_clusters
        }
        
        print(f"Volumen montado: '{label}' | Clusters Totales: {total_clusters} | Tamaño Cluster: {cluster_size} bytes")
        
        # Tras validar leemos los archivos existentes
        self._parse_directory()

    def _parse_directory(self):
        print("Parseando clústeres del directorio...")
        self.directory = {}
        
        dir_clusters = self.metadata.get('dir_clusters', 8)
        
        # El directorio vive en los clusters del 1 al dir_clusters
        for cluster_id in range(1, dir_clusters + 1):
            cluster_data = self.worker.read_cluster(cluster_id)
            
            # Dividir los 2048 bytes del cluster en ranuras de 64 bytes
            for offset in range(0, 2048, 64):
                entry = cluster_data[offset:offset+64]
                
                # Extraer Tipo (byte 0)
                file_type = entry[0:1].decode('ascii')
                
                # Extraer Nombre (bytes 1 a 15)
                filename_raw = entry[1:16].decode('ascii')
                filename = filename_raw.rstrip(' \x00') # Remover relleno nulo o espacios
                
                # Validar ranura ocupada vs ranura libre
                if file_type == '/' or filename == '###############':
                    continue
                    
                # Extraer Tamaño (16-20) y Cluster Inicial (20-23)
                file_size = struct.unpack('<I', entry[16:20])[0]
                start_cluster = struct.unpack('<I', entry[20:24])[0]
                
                # Extraer fechas (30-44 y 50-64)
                ctime_raw = entry[30:45].decode('ascii').strip('\x00')
                mtime_raw = entry[50:65].decode('ascii').strip('\x00')
                
                # Función auxiliar para convertir fecha a Timestamp POSIX
                def parse_date(date_str):
                    try:
                        return time.mktime(time.strptime(date_str, '%Y%m%d%H%M%S'))
                    except ValueError:
                        return time.time() # Si falla, devolver fecha actual
                
                ctime = parse_date(ctime_raw)
                mtime = parse_date(mtime_raw)
                
                # Guardar el archivo en la caché para consultas veloces
                self.directory[filename] = {
                    'size': file_size,
                    'start_cluster': start_cluster,
                    'ctime': ctime,
                    'mtime': mtime,
                    # Guardamos su ubicación exacta por si después el usuario decide eliminarlo
                    'meta_cluster_id': cluster_id,
                    'meta_offset': offset
                }

                print(f"    -> Encontrado: {filename} ({file_size} bytes, Clúster Inicial: {start_cluster})")

    def getattr(self, path, fh=None):
        # El SO pregunta atributos del archivo o directorio
        if path == '/':
            # Simulamos que la raíz es un directorio válido con todos los permisos
            return {
                'st_mode': (stat.S_IFDIR | 0o755),
                'st_nlink': 2
            }
        
        filename = path.lstrip('/')
        if filename in self.directory:
            f_info = self.directory[filename]
            return {
                'st_mode': (stat.S_IFREG | 0o666), # Indicamos que es un archivo regular
                'st_nlink': 1,
                'st_size': f_info['size'],
                'st_ctime': f_info['ctime'],
                'st_mtime': f_info['mtime'],
                'st_atime': f_info['mtime']
            }
        raise OSError(errno.ENOENT, os.strerror(errno.ENOENT))


    def readdir(self, path, fh):
        # El SO hace un comando 'ls'
        # Siempre debemos devolver el directorio actual y el padre
        dirents = ['.', '..']

        if path == '/':
            # Proyectar las llaves (nombres de archivos) de nuestra caché
            dirents.extend(self.directory.keys())

        for r in dirents:
            yield r
