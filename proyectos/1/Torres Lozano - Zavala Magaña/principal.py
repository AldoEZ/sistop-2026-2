"""
principal.py — Punto de entrada del programa FiUnamFS

El menú ya quedó. Los hilos y la sincronización
con semáforos todavía estan pendienntes.
"""

import sys
from sistema_archivos import FiUnamFS, validar_imagen
from utilidades import limpiar_pantalla, imprimir_encabezado, imprimir_error, imprimir_info

fs = None

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
    print(f"Sistema cargado: {fs.nombre} v{fs.version} — {fs.etiqueta}")
    print(f"Clusters: {fs.total_clusters} totales, {fs.clusters_dir} de directorio")
    print(f"Max entradas en directorio: {fs.max_entradas}\n")

  # Zavala URGENTE La rúbrica pide "por lo menos dos hilos operando concurrentemente".
    # Hay que hacer que menú corra en el hilo principal y que las operaciones
    # principales (copiar, listar, borrar) las mandemos a un otro hilo
       
    # Menu sencillo, sin hilos todavía
    while True:
        limpiar_pantalla()
        imprimir_encabezado("Menú Principal")
        print("  (1) Listar archivos del directorio")
        print("  (2) Copiar archivo desde FiUnamFS a mi computadora")
        print("  (3) Copiar archivo desde mi computadora a FiUnamFS")
        print("  (4) Eliminar un archivo de FiUnamFS")
        print("  (5) Salir\n")
        opcion = input("  Opción → ").strip()

        if opcion == "5":
            imprimir_info("\n  ¡Adios!\n")
            break
        else:
            # Conectar cada opción con los métodos de fs.
            # por ejm si es 1, llamar a fs.listar_archivos, si es 2 pedir nombres y llamar fs.copiar_a_local y  así.
            imprimir_info("  Pendiente")
            input("  Presiona Enter para continuar...")

if __name__ == "__main__":
    main()
