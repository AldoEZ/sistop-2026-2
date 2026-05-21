"""
Proyecto (Micro) sistema de archivos multihiloss
Autores: 
    - Gonzalez Falcon Luis Adrían
    - Lopez Morales Fernando Samuel
Entrega 2026-05-21
"""

import threading
import time
import struct
import sys, os, stat, errno
import fuse 
from fuse import Fuse

from fiunamfs import FiUnamFS

# Versión de api de python para FUSE
fuse.fuse_python_api = (0, 2)

orden_actual = {"comando": None, "argumentos": []}
sistema_corriendo = True

#mutex para proteger el disco
mutex_fs = threading.Semaphore(1)

#semaforos sincronización
sem_orden_pendiente = threading.Semaphore(0)
sem_orden_terminada = threading.Semaphore(0)


#Hilo secundario que actúa cuando sucede algún evento
def hilo_trabajador(motor_fs):
    global sistema_corriendo, orden_actual
    
    #print("\nHilo TRABAJADOR iniciado y esperando...")
    
    while sistema_corriendo:
        
        #Hilo trabajador adquiere se queda en espera hasta que la interfaz suelte el mutex.
        sem_orden_pendiente.acquire()
        
        if not sistema_corriendo:
            #print("Hilo TRABAJADOR saliendo")
            break
        
        #print("Hilo TRABAJADOR despierta")
        comando = orden_actual["comando"]
        args = orden_actual["argumentos"]
        
        # Hilo bloquea el disco para realizar una exclusión
        #print("Hilo TRABAJADOR adquiere el mutex del disco para que nadie más lo use")
        mutex_fs.acquire()
        
        try:
            orden_actual["resultado"] = -errno.EIO
            if comando == "listar_fuse":
                orden_actual["resultado"] = motor_fs.listar_directorio()
            elif comando == "eliminar_fuse":
                # Intentamos eliminar, si falla atrapamos el error para FUSE
                try:
                    motor_fs.eliminar_archivo(args[0])
                    orden_actual["resultado"] = 0 # 0 en Unix significa "éxito"
                except FileNotFoundError:
                    orden_actual["resultado"] = -errno.ENOENT
        except Exception as e:
            sys.stderr.write(f"[Trabajador] Error: {e}\n")
        finally:
            mutex_fs.release()
        
        # Le avisamos a la interfaz que ya terminamos el trabajo
        sem_orden_terminada.release()
class FiUnamFS_FUSE(Fuse):
    def __init__(self, *args, **kw):
        fuse.Fuse.__init__(self, *args, **kw)
        
        # Obtiene los identificadores del usuario actual
        self.uid = os.getuid()
        self.gid = os.getgid()

    def getattr(self, path: str):
        st = fuse.Stat()
        
        # pertencera al usuario que montó el sistema
        st.st_uid = self.uid
        st.st_gid = self.gid

        if path == '/':
            st.st_mode = stat.S_IFDIR | 0o777
            st.st_nlink = 2
            return st

        nombre_archivo = path[1:]
        
        global orden_actual
        orden_actual["comando"] = "listar_fuse"
        sem_orden_pendiente.release()
        sem_orden_terminada.acquire()
        
        archivos = orden_actual["resultado"]

        if nombre_archivo in archivos:
            meta = archivos[nombre_archivo]
            st.st_mode = stat.S_IFREG | 0o666
            st.st_nlink = 1
            st.st_size = meta['tamano']
            st.st_ctime = meta['c_time']
            st.st_mtime = meta['m_time']
            st.st_atime = meta['m_time']
            return st

        return -errno.ENOENT

    def readdir(self, path: str, offset: int):
        if path == '/':
            global orden_actual
            orden_actual["comando"] = "listar_fuse"
            sem_orden_pendiente.release()
            sem_orden_terminada.acquire()
            
            archivos = orden_actual["resultado"]
            
            # COmo en la clase
            for r in ['.', '..'] + list(archivos.keys()):
                yield fuse.Direntry(r)
    def unlink(self, path: str):
        """
        Elimina un archivo. Invocado por el comando 'rm' que detona la llamada unlink()
        """
        nombre_archivo = path[1:]
        
        global orden_actual
        orden_actual["comando"] = "eliminar_fuse"
        orden_actual["argumentos"] = [nombre_archivo]
        
        # Sincronización con el trabajador
        sem_orden_pendiente.release()
        sem_orden_terminada.acquire()
        
        # 0: exitoso || -errno si fallo
        return orden_actual["resultado"]

#Hilo principal que va a contener la funcionalidad de la interfaz
def main():
    global sistema_corriendo, orden_actual
    
    #print("========= INICIANDO PROYECTO 1 =========")
    
    if len(sys.argv) < 2 or sys.argv[1] == '--help':
        print("Uso: python3 fiunamfs_fuse.py <punto_montaje>")
        sys.exit(1)

    sys.argv.insert(1, '-f')
    #trycatch por si hay un dato que no es válido
    try:
        motor = FiUnamFS("./fiunamfs.img")
        motor.conectar()
        #motor.validar_superbloque()
    except Exception as e:
        print(f"Error al iniciar: {e}")
        return

    trabajador = threading.Thread(target=hilo_trabajador, args=(motor,))
    trabajador.start()
    time.sleep(0.2)
    
    server = FiUnamFS_FUSE(version="%prog " + fuse.__version__,
                           usage="Montaje FiUnamFS mediante FUSE",
                           dash_s_do='setsingle')
    server.parse(errex=1)
    
    try:
        server.main()
    finally:
        sistema_corriendo = False
        sem_orden_pendiente.release()
        trabajador.join()
        motor.desconectar()

if __name__ == "__main__":
    main()