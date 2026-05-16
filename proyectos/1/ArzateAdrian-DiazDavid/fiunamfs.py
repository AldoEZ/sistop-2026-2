import os
import stat
import errno
from fuse import Operations, LoggingMixIn

class FiUnamFS(LoggingMixIn, Operations):
    """
    Capa Productora: Recibe llamadas del sistema operativo vía FUSE 
    y encola tareas al Worker.
    """
    def __init__(self, worker):
        self.worker = worker
        # lógica para la lectura del clúster 0 (Superbloque) y el directorio.

    def getattr(self, path, fh=None):
        # El SO pregunta atributos del archivo o directorio
        if path == '/':
            # Simulamos que la raíz es un directorio válido con todos los permisos
            return {
                'st_mode': (stat.S_IFDIR | 0o755),
                'st_nlink': 2
            }
        
        # Todo lo que no sea el directorio raíz fingimos que no existe 
        raise OSError(errno.ENOENT, os.strerror(errno.ENOENT))


    def readdir(self, path, fh):
        # El SO hace un comando 'ls'
        # Siempre debemos devolver el directorio actual y el padre
        dirents = ['.', '..']
        
        # Iterar sobre caché del directorio en memoria para devolver los archivos
        for r in dirents:
            yield r
