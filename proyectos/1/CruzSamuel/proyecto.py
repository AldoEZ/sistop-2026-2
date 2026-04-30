#!/usr/bin/env python3
"""
Proyecto 1 — FiUnamFS.
Por ahora solo defino las constantes del layout físico del disco.
"""

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
