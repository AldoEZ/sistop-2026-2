"""
principal.py — Punto de entrada del programa FiUnamFS

Ya tenemos el hilo _listar funcionando con semáforos.
Las opciones de copiar y eliminar todavía están en desarrollo.
"""

import sys
import threading

from sistema_archivos import FiUnamFS, validar_imagen
from utilidades import (
    limpiar_pantalla, imprimir_encabezado,
    imprimir_error, imprimir_info, formatear_tamano
)

opcion: str = ""
fs: FiUnamFS | None = None


def _menu(sem_menu, sem_listar, sem_local, sem_fs, sem_eliminar):
    """Hilo del menú. Por ahora solo el listar está conectado."""
    global opcion

    while True:
        sem_menu.acquire()
        limpiar_pantalla()
        imprimir_encabezado("Menú Principal")
        print("  (1) Listar archivos del directorio")
        print("  (2) Copiar archivo desde FiUnamFS a mi computadora  [en desarrollo]")
        print("  (3) Copiar archivo desde mi computadora a FiUnamFS  [en desarrollo]")
        print("  (4) Eliminar un archivo de FiUnamFS                 [en desarrollo]")
        print("  (5) Salir\n")
        opcion = input("  Opción → ").strip()
        # Luis tenemos el esqueleto de la concurrencia ya bien.
        # Cuando implementemos las funciones de copiado/borrado en el sistema_archivos,
        # solo agregar los elif aquí (opcion == "2": sem_local.release y así).

        if   opcion == "1": sem_listar.release()
        elif opcion == "5":
            sem_listar.release()
            sem_local.release()
            sem_fs.release()
            sem_eliminar.release()
            break
        else:
            imprimir_info("  Opción en desarrollo, intenta con (1) o (5).")
            sem_menu.release()


def _listar(sem_menu, sem_listar):
    """Hilo que lista los archivos del directorio."""
    global opcion, fs

    while True:
        sem_listar.acquire()
        if opcion == "5":
            break

        limpiar_pantalla()
        imprimir_encabezado("Archivos en FiUnamFS")

        archivos = fs.listar_archivos()
        if not archivos:
            imprimir_info("  El directorio está vacío.")
        else:
            # Quedó muy bien la tabla. Con la función de formatear_tamano 
            # se ve muy pro. Ya tenemos cubierta una de las opciones principales.
            print(f"  {'#':<4} {'Nombre':<16} {'Tamaño':>10}   {'Creación'}")
            print(f"  {'─'*4} {'─'*16} {'─'*10}   {'─'*19}")
            for i, archivo in enumerate(archivos, 1):
                print(f"  {i:<4} {archivo.name:<16} {formatear_tamano(archivo.size):>10}   {archivo.creation_date}")

        input("\n  Presiona Enter para continuar...")
        sem_menu.release()


def _pendiente(sem_menu, sem):
    """Hilo temporal para opciones aún no implementadas."""
    global opcion
    while True:
        sem.acquire()
        if opcion == "5":
            break
        # zavala estos hilos temporales los vamos a reemplazar en el sig commit
        # por _copiar_a_local, _copiar_a_fs, y _eliminar. 
        # Aquí vamos a pedir los inputs (nombres de archivos) y llamar a las funciones del archivo de fs.
        sem_menu.release()


def main():
    global fs

    if len(sys.argv) != 2:
        imprimir_error("Uso: python principal.py <ruta_a_fiunamfs.img>")
        sys.exit(1)

    ruta_imagen = sys.argv[1]

    if not validar_imagen(ruta_imagen):
        imprimir_error(f'El archivo "{ruta_imagen}" no es una imagen FiUnamFS válida.')
        sys.exit(1)

    fs = FiUnamFS(ruta_imagen)
    # Bien inicializados en 0 para bloquear los hilos 
    # de trabajo hasta que el menú los despierte"

    sem_menu     = threading.Semaphore(1)
    sem_listar   = threading.Semaphore(0)
    sem_local    = threading.Semaphore(0)
    sem_fs       = threading.Semaphore(0)
    sem_eliminar = threading.Semaphore(0)

    hilos = [
        threading.Thread(target=_menu,     args=(sem_menu, sem_listar, sem_local, sem_fs, sem_eliminar), daemon=True),
        threading.Thread(target=_listar,   args=(sem_menu, sem_listar),   daemon=True),
        threading.Thread(target=_pendiente,args=(sem_menu, sem_local),    daemon=True),
        threading.Thread(target=_pendiente,args=(sem_menu, sem_fs),       daemon=True),
        threading.Thread(target=_pendiente,args=(sem_menu, sem_eliminar), daemon=True),
    ]

    for hilo in hilos:
        hilo.start()

    hilos[0].join()
    imprimir_info("\n  ¡Hasta luego!\n")


if __name__ == "__main__":
    main()
