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
   
    pass

class FS(threading.Thread):


    pass




def main():
    ruta_img = 'fiunamfs.img' 
    
    if not os.path.exists(ruta_img):
        print(f"No se encontró el archivo '{ruta_img}'.")
        return

    # Inicialización de hilos y sincronización
    cola_peticiones = queue.Queue()
    #hilo_fs = FS(ruta_img, cola_peticiones)
    #hilo_fs.start()
    
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
            cola_peticiones.put(PeticionFS('SALIR'))
            print("Vuelva pronto!")
            break
        else:
            print("Opción inválida.")
            continue
            
        # cola_peticiones.put(peticion)
        # peticion.evento.wait() 
        
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


