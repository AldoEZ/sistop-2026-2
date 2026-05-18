#!/usr/bin/env python3
"""
Inicio de proyecto FiUnamFS

En este punto aun no se monta FUSE, por lo que no modificamos la imagen "fiunamfs.img",
pero dejamos el ambiente preparado para montar FiUnamFS con FUSE.
"""
from pathlib import Path # libreria para manejo de rutas de archivos
import sys

from constantes import NOMBRE_SISTEMA, VERSION
from argumentos import crear_parser, validar_rutas
from fiunamfs import FiUnamFS

def main():
    parser = crear_parser()
    args = parser.parse_args()
    
    ruta_imagen = Path(args.imagen).resolve()
    ruta_montaje = Path(args.montaje).resolve()
    
    if not validar_rutas(ruta_imagen, ruta_montaje):
        return 1
    
    sistema = FiUnamFS(ruta_imagen)
    if not sistema.validar_superbloque():
        return 1
    
    if args.listar:
        archivos = sistema.listar_archivos()
        
        print("\nConteido del directorio:")
        if not archivos:
            print("No hay archivos registrados")
        else:
            for archivo in archivos:
                print(
                    f"- {archivo.nombre_archivo} | "
                    f"{archivo.tamano} | "
                    f"cluster inicial: {archivo.cluster_inicial} | "
                    f"fecha creacion: {archivo.fecha_creacion} | "
                    f"ultima modificacion: {archivo.fecha_modificacion}"
                )
    elif args.leer:
        contenido = sistema.leer_archivo(args.leer)
        
        if contenido is None:
            return 1
        
        print(f"El contenido del archivo '{args.leer} es:'")
        print(contenido.decode("ascii", errors="replace"))
    elif args.extraer:
        ruta_destino = Path(args.destino).resolve()
        
        if not sistema.extraer_archivo(args.extraer, ruta_destino):
            return 1
    elif args.eliminar:
        if not sistema.eliminar_archivo(args.eliminar):
            return 1
    else:
        print("No se indico ninguna accion")
        print("Usar --listar, --leer ARCHIVO, --extraer ARCHIVO o --eliminar ARCHIVO")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
