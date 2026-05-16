"""
Constantes generales de  FiUnamFS
"""

# disco
TAM_DISCO = 1440 * 1024

# cluster
TAM_SECTOR = 512
SECTORES_POR_CLUSTER = 4
TAM_CLUSTER = TAM_SECTOR * SECTORES_POR_CLUSTER

# identificadores de clusters
CLUSTER_SUPERBLOQUE = 0
CLUSTER_INICIO_DIRECTORIO = 1
CLUSTER_FINAL_DIRECTORIO = 8

TAM_ENTRADA_DIRECTORIO = 64

# informacion en superbloque
NOMBRE_SISTEMA = "FiUnamFS"
VERSION = "26-2"

# especificaciones entrada y tipo de archivo
ENTRADA_VACIA = "###############"
TIPO_ARCHIVO = "-"
TIPO_ENTRADA_VACIA = "/"
