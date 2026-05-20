import os
import struct
import threading
import queue
import time
from datetime import datetime


class PeticionFS:
    def __init__(self, accion, *args):
        self.accion = accion
        self.args = args
        self.resultado = None
        self.evento = threading.Event()


class FS(threading.Thread):
    def __init__(self, ruta_img, cola_peticiones):
        super().__init__()
        self.ruta_img = ruta_img
        self.cola_peticiones = cola_peticiones
        self.daemon = True  # Se cierra cuando el hilo principal termina
        self.lock_archivo = threading.Lock() 
        
    def run(self):
        while True:
            peticion = self.cola_peticiones.get()
            
            # Operaciones sobre el disco
            with self.lock_archivo:
                try:
                    self.validar_version()
                    if peticion.accion == 'LISTAR':
                        peticion.resultado = self.listar_archivos()
                    elif peticion.accion == 'COPIAR_FUERA':
                        peticion.resultado = self.copiar_fuera(peticion.args[0], peticion.args[1])
                    elif peticion.accion == 'COPIAR_DENTRO':
                        peticion.resultado = self.copiar_dentro(peticion.args[0], peticion.args[1])
                    elif peticion.accion == 'ELIMINAR':
                        peticion.resultado = self.eliminar_archivo(peticion.args[0])
                except Exception as e:
                    peticion.resultado = f"Error del sistema: {e}"
            
            peticion.evento.set() 
            self.cola_peticiones.task_done()

    def validar_version(self):
        with open(self.ruta_img, 'rb') as f:
            f.seek(5)
            nombre = f.read(8)
            if nombre != b'FiUnamFS':
                raise ValueError("FiUnamFS no válido.")
            f.seek(14)
            version = f.read(4)
            if version != (b'24-2' or b'26-2'):
                raise ValueError("Versión de FiUnamFS no soportada.")
        
        
    def listar_archivos(self):
        
        
        pass
        
    
    def copiar_fuera(self):
        
        
        pass
    
    
    def copiar_dentro(self):
        
        
        pass


    def eliminar_archivo(self):
        
        
        pass


def main():
    ruta_img = 'fiunamfs.img'
    
    if not os.path.exists(ruta_img):
        print(f"No se encontró el archivo '{ruta_img}'.")
        return

    # Inicialización de hilos y sincronización
    cola_peticiones = queue.Queue()
    hilo_fs = FS(ruta_img, cola_peticiones)
    hilo_fs.start()
    
    print("---FiUnamFS---")
    
    while True:
        print("\nElija una opción:")
        print("1.- Listar")
        print("2.- Copiar a mi PC")
        print("3.- Copiar a FS ")
        print("4.- Eliminar")
        print("5.- Salir")
        opcion = input("Selecciona una operación: ").strip()
        
        peticion = None
        if opcion == '1':
            peticion = PeticionFS('LISTAR')
        elif opcion == '2':
            nombre = input("Nombre del archivo en FiUnamFS: ")
            ruta = input("Nombre que tendra del archivo en PC: ")
            peticion = PeticionFS('COPIAR_FUERA', nombre, ruta)
        elif opcion == '3':
            ruta = input("Nombre del archivo en PC: ")
            nombre = input("Nombre que tendra el archivo en FiUnamFS: ")
            peticion = PeticionFS('COPIAR_DENTRO', ruta, nombre)
        elif opcion == '4':
            nombre = input("Nombre del archivo a eliminar en FiUnamFS: ")
            peticion = PeticionFS('ELIMINAR', nombre)
        elif opcion == '5':
            print("Vuelva pronto!")
            break
        else:
            print("Opción inválida.")
            continue
            
        #   Se envía a la cola y espera a que el evento se active (sincronización)
        cola_peticiones.put(peticion)
        peticion.evento.wait() 
        
        # Procesa los resultados devueltos por el hilo
        if opcion == '1':
            archivos = peticion.resultado
            if isinstance(archivos, list):
                print(f"\n{'Nombre':<16} | {'Tamaño':<10} | {'Cluster':<7} | {'Fecha Creación'}")
                print("-" * 60)
                for arch in archivos:
                    print(f"{arch['nombre']:<16} | {arch['tamano']:<10} | {arch['cluster']:<7} | {arch['creacion']}")
            else:
                print(archivos)
        else:
            print(peticion.resultado)

if __name__ == '__main__':
    main()




