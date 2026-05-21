#!/usr/bin/python3

#Programa principal, se encarga de implementar FUSE para conectar con todo el resto del sistema
#Autores: Isaac Campos, Alejandro Martinez
#Fecha de realización: 19 Mayo 2026

import fuse
import stat
import errno
import sys
import os
from datetime import datetime
from fiunamfs.disco import Disco
from fuse import Fuse

fuse.fuse_python_api = (0, 2)

class FiUnamFs(Fuse):

    ruta_img = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._disco = None

    @property
    def disco(self):
        if self._disco is None:
            self._disco = Disco(self.ruta_img)
        return self._disco
        
    
    def readdir(self, path:str, offset:int):
        for r in [ '.', '..' ] + list(self.disco.listarEntradas()):
            yield fuse.Direntry(r)

    def getattr(self, path:str):
        st = fuse.Stat()

        st.st_uid = os.getuid()   
        st.st_gid = os.getgid()   

        if path == '/':
            st.st_mode = stat.S_IFDIR | 0o755
            st.st_nlink = 2
            return st

        else:
            nombre = path.lstrip('/')
            entrada = self.disco.encontrarEntrada(nombre)
            if entrada != None:
                st.st_mode = stat.S_IFREG | 0o755
                st.st_nlink = 1
                st.st_size = entrada.tam_archivo
                cadena_fecha = entrada.hf_creado
                if len(cadena_fecha) == 14 and cadena_fecha.isdigit():
                    fecha_creacion = datetime.strptime(cadena_fecha, '%Y%m%d%H%M%S')
                    marca_tiempo = int(fecha_creacion.timestamp())
                else:
                    marca_tiempo = 0

                st.st_mtime = marca_tiempo
                st.st_ctime = marca_tiempo
                st.st_atime = marca_tiempo
                return st

        return -errno.ENOENT

    def read(self, path: str, size: int, offset: int) -> bytes:
        contenido = self.disco.leerEntrada(path.lstrip('/'))
        if contenido != None:
            slen = len(contenido)
            if offset < slen:
                if offset + size > slen:
                    size = slen - offset
                buf = contenido[offset:offset+size]
            else:
                # If reading beyond the end of the file, return an empty
                # byte string.
                buf = b''

            return buf
        else:
            return -errno.ENOENT


    def truncate(self, path, length):
        return 0

    def unlink(self, path: str):
        nombre = path.lstrip('/')
        if self.disco.encontrarEntrada(nombre) is not None:
            self.disco.eliminarEntrada(nombre)
            return 0
        else:
            return -errno.ENOENT

    def create(self, path:str, flags, mode):
        nombre = path.lstrip('/')
        if self.disco.encontrarEntrada(nombre):
            return -errno.EEXIST
        self.disco.escribirEntrada(nombre, b'')
        return 0
    
    def open(self, path, flags):
        nombre = path.lstrip('/')
        if self.disco.encontrarEntrada(nombre) is None:
            return -errno.ENOENT
        return 0

    def write(self, path, buf, offset):
        nombre = path.lstrip('/')
        entrada = self.disco.encontrarEntrada(nombre)
        if entrada is None:
            return -errno.ENOENT
        contenido = self.disco.leerEntrada(nombre)
        if contenido is None:
            contenido = b''
        nuevo = bytearray(contenido)
        if offset > len(nuevo):
            nuevo.extend(b'\x00' * (offset - len(nuevo)))
        nuevo[offset:offset+len(buf)] = buf
        self.disco.sobrescribirEntrada(nombre, bytes(nuevo))
        return len(buf)
    


def main():
    if len(sys.argv) < 3:
        sys.argv.append('--help')

    title = 'Proyecto - Mini Sistema de Archivos con FUSE'
    descr = ("Lee la imagen de un disco y permite montarlo al igual que realizar operaciones sobre el sistema")

    FiUnamFs.ruta_img = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else None

    usage = ("\n\nProyecto: Mini Sistema de Archivos con FUSE\n  %s: %s\n\n%s\n\n%s" %
             (sys.argv[0], title, descr, fuse.Fuse.fusage))

    server = FiUnamFs(version="%prog " + fuse.__version__,
                                 usage=usage,
                                 dash_s_do='setsingle')

    server.parse(errex=1)
    server.main()

if __name__ == '__main__':
    main()
