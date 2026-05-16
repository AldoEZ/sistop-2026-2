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

"""
Funcion auxiliar para mostrar la configuracion inicial
"""
def configuracion_inicial(ruta_imagen, ruta_montaje):
    print(f"{NOMBRE_SISTEMA} versión {VERSION}")
    print("Inicializando micro sistema de archivos...")
    print(f"Imagen: {ruta_imagen}")
    print(f"Punto de montaje: {ruta_montaje}")

def main():
    parser = crear_parser()
    args = parser.parse_args()
    
    ruta_imagen = Path(args.imagen).resolve()
    ruta_montaje = Path(args.montaje).resolve()
    
    if not validar_rutas(ruta_imagen, ruta_montaje):
        return 1
    
    configuracion_inicial(
        ruta_imagen,
        ruta_montaje
    )
    
    print("Configuracion inicial correcta.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
