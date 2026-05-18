"""
interfaz de FUSE para montar FiUnamFS

montaje de lectura con fuse para listar archivos, 
consultar atributos y leer contenido
"""

import errno
import stat
import fuse

from fuse import Fuse
fuse.fuse_python_api = (0,2)

"""
sistema FiUnamFS con fuse
"""
class SistemaFuse(Fuse):
    def __init__(self, fiunamfs, *args, **kwargs):
        Fuse.__init__(self, *args, **kwargs)
        self.fiunamfs = fiunamfs
    
    """
    listar el contenido del directorio raiz
    """
    def readdir(self, path, offset):
        if path != "/":
            return -errno.ENOENT
        
        for entrada in [".", ".."]:
            yield fuse.Direntry(entrada)
        
        archivos = self.fiunamfs.listar_archivos()
        
        for archivo in archivos:
            yield fuse.Direntry(archivo.nombre_archivo)
    
    """
    obtener atributos de un archivo o directorio
    """
    def getattr(self, path):
        st = fuse.Stat()
        
        if path == "/":
            st.st_mode = stat.S_IFDIR | 0o755
            st.st_nlink = 2
            return st
        
        nombre_archivo = path[1:]
        entrada = self.fiunamfs.buscar_archivo(nombre_archivo)
        
        if entrada is None:
            return -errno.ENOENT
        
        st.st_mode = stat.S_IFREG | 0o644
        st.st_nlink = 1
        st.st_size = entrada.tamano
        
        return st
    
    """
    lectura de un archivo de FiUnamFS
    """
    def read(self, path, size, offset):
        nombre_archivo = path[1:]
        contenido = self.fiunamfs.leer_archivo(nombre_archivo, size, offset)
        
        if contenido is None:
            return -errno.ENOENT
        
        return contenido
    
    """
    elimina un archivo desde el montaje de FUSE
    """
    def unlink(self, path):
        nombre_archivo = path[1:]
        
        if not self.fiunamfs.eliminar_archivo(nombre_archivo):
            return -errno.ENOENT
        return 0
