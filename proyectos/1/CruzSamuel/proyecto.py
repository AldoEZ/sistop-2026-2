#!/usr/bin/env python3
"""
Proyecto 1 — FiUnamFS.
Etapa 2: leer el directorio plano y descartar entradas libres.
"""

import os
import struct
import sys
from dataclasses import dataclass
from datetime import datetime


# Tamaños base
TAMANIO_SECTOR = 512
SECTORES_POR_CLUSTER = 4
TAMANIO_CLUSTER = TAMANIO_SECTOR * SECTORES_POR_CLUSTER  # 2048
TAMANIO_IMAGEN = 1440 * 1024
TOTAL_CLUSTERS = TAMANIO_IMAGEN // TAMANIO_CLUSTER

# Identificación del sistema de archivos
OFFSET_NOMBRE_FS = 5
LONGITUD_NOMBRE_FS = 8
NOMBRE_FS_ESPERADO = b'FiUnamFS'

OFFSET_VERSION_FS = 14
LONGITUD_VERSION_FS = 4
VERSION_FS_ESPERADA = b'26-2'

# Directorio plano: clústeres 1 a 8, entradas de 64 bytes
CLUSTER_INICIO_DIRECTORIO = 1
NUM_CLUSTERS_DIRECTORIO = 8
TAMANIO_ENTRADA = 64

# Layout de una entrada (verificado contra la imagen de muestra):
#   byte  0      : tipo ('-' archivo, '/' entrada libre)
#   bytes 1-14   : nombre (14 chars ASCII)
#   bytes 16-19  : tamaño (uint32 LE)
#   bytes 20-23  : clúster inicial (uint32 LE)
#   bytes 30-43  : fecha de creación 'AAAAMMDDHHmmss'
#   bytes 50-63  : fecha de modificación 'AAAAMMDDHHmmss'
OFFSET_TIPO = 0
OFFSET_NOMBRE = 1
LONGITUD_NOMBRE = 14
OFFSET_TAMANIO = 16
OFFSET_CLUSTER_INICIAL = 20
OFFSET_FECHA_CREACION = 30
OFFSET_FECHA_MODIFICACION = 50
LONGITUD_FECHA = 14

TIPO_ARCHIVO = b'-'
TIPO_ENTRADA_LIBRE = b'/'
RELLENO_NOMBRE_LIBRE = 0x23  # '#'


@dataclass
class EntradaDirectorio:
    nombre: str
    tamanio: int
    cluster_inicial: int
    fecha_creacion: datetime
    fecha_modificacion: datetime


def validar_imagen(ruta):
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


def _decodificar_fecha(crudo):
    try:
        return datetime.strptime(crudo.decode('ascii'), '%Y%m%d%H%M%S')
    except (ValueError, UnicodeDecodeError):
        return None


def _es_entrada_libre(bloque):
    if bloque[OFFSET_TIPO:OFFSET_TIPO + 1] == TIPO_ENTRADA_LIBRE:
        return True
    nombre = bloque[OFFSET_NOMBRE:OFFSET_NOMBRE + LONGITUD_NOMBRE]
    return all(b == RELLENO_NOMBRE_LIBRE for b in nombre)


def _parsear_entrada(bloque):
    nombre = (bloque[OFFSET_NOMBRE:OFFSET_NOMBRE + LONGITUD_NOMBRE]
              .decode('ascii', errors='replace')
              .rstrip(' \x00'))
    (tamanio,) = struct.unpack_from('<I', bloque, OFFSET_TAMANIO)
    (cluster,) = struct.unpack_from('<I', bloque, OFFSET_CLUSTER_INICIAL)
    creacion = _decodificar_fecha(
        bloque[OFFSET_FECHA_CREACION:OFFSET_FECHA_CREACION + LONGITUD_FECHA]
    )
    modificacion = _decodificar_fecha(
        bloque[OFFSET_FECHA_MODIFICACION:OFFSET_FECHA_MODIFICACION + LONGITUD_FECHA]
    )
    return EntradaDirectorio(
        nombre=nombre,
        tamanio=tamanio,
        cluster_inicial=cluster,
        fecha_creacion=creacion,
        fecha_modificacion=modificacion,
    )


def leer_directorio(ruta):
    """Devuelve las entradas activas (no libres) del directorio."""
    with open(ruta, 'rb') as f:
        f.seek(CLUSTER_INICIO_DIRECTORIO * TAMANIO_CLUSTER)
        crudo = f.read(NUM_CLUSTERS_DIRECTORIO * TAMANIO_CLUSTER)

    entradas = []
    for i in range(len(crudo) // TAMANIO_ENTRADA):
        bloque = crudo[i * TAMANIO_ENTRADA:(i + 1) * TAMANIO_ENTRADA]
        if _es_entrada_libre(bloque):
            continue
        entradas.append(_parsear_entrada(bloque))
    return entradas


def main():
    if len(sys.argv) != 2:
        print('Uso: python3 proyecto.py <ruta_imagen>')
        return 1
    try:
        validar_imagen(sys.argv[1])
        entradas = leer_directorio(sys.argv[1])
        print(f'Encontradas {len(entradas)} entradas activas:')
        for e in entradas:
            print(f'  {e.nombre!r}  {e.tamanio} bytes  cluster={e.cluster_inicial}')
    except (FileNotFoundError, ValueError) as err:
        print(f'Error: {err}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
