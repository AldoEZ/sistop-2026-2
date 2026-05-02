#!/usr/bin/env python3
"""
Proyecto 1 — FiUnamFS.
Primera etapa: validar que la imagen tenga la firma y la versión correctas.
"""

import os
import struct
import sys


# Tamaños base
TAMANIO_SECTOR = 512
SECTORES_POR_CLUSTER = 4
TAMANIO_CLUSTER = TAMANIO_SECTOR * SECTORES_POR_CLUSTER  # 2048
TAMANIO_IMAGEN = 1440 * 1024
TOTAL_CLUSTERS = TAMANIO_IMAGEN // TAMANIO_CLUSTER

# Identificación del sistema de archivos (en el superbloque)
OFFSET_NOMBRE_FS = 5
LONGITUD_NOMBRE_FS = 8
NOMBRE_FS_ESPERADO = b'FiUnamFS'

OFFSET_VERSION_FS = 14
LONGITUD_VERSION_FS = 4
VERSION_FS_ESPERADA = b'26-2'


def validar_imagen(ruta):
    """Comprueba tamaño, firma y versión de la imagen FiUnamFS."""
    if not os.path.isfile(ruta):
        raise FileNotFoundError(f'No existe la imagen «{ruta}».')
    if os.path.getsize(ruta) != TAMANIO_IMAGEN:
        raise ValueError(
            f'La imagen mide {os.path.getsize(ruta)} bytes; se esperaban '
            f'{TAMANIO_IMAGEN}.'
        )

    with open(ruta, 'rb') as f:
        superbloque = f.read(TAMANIO_CLUSTER)

    (firma,) = struct.unpack_from(
        f'{LONGITUD_NOMBRE_FS}s', superbloque, OFFSET_NOMBRE_FS
    )
    if firma != NOMBRE_FS_ESPERADO:
        raise ValueError(
            f'Firma inválida: se esperaba «{NOMBRE_FS_ESPERADO.decode()}», '
            f'se encontró «{firma.decode(errors="replace")}».'
        )

    (version,) = struct.unpack_from(
        f'{LONGITUD_VERSION_FS}s', superbloque, OFFSET_VERSION_FS
    )
    if version != VERSION_FS_ESPERADA:
        raise ValueError(
            f'Versión incompatible: se esperaba «{VERSION_FS_ESPERADA.decode()}», '
            f'se encontró «{version.decode(errors="replace")}».'
        )


def main():
    if len(sys.argv) != 2:
        print('Uso: python3 proyecto.py <ruta_imagen>')
        return 1
    try:
        validar_imagen(sys.argv[1])
    except (FileNotFoundError, ValueError) as err:
        print(f'Error: {err}', file=sys.stderr)
        return 1
    print('Imagen FiUnamFS válida.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
