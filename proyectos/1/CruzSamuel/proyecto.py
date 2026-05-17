#!/usr/bin/env python3
"""
Proyecto 1 — FiUnamFS.
Etapa 9: interfaz de linea de comandos con argparse y subcomandos.
"""

import argparse
import math
import os
import struct
import sys
import threading
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

CLUSTER_INICIO_DATOS = CLUSTER_INICIO_DIRECTORIO + NUM_CLUSTERS_DIRECTORIO


# Un único Lock global serializa todo acceso a la imagen. Cada operación
# que toca el directorio o el área de datos lo hace dentro de un bloque
# `with cerrojo:`, garantizando que la decisión de dónde escribir y la
# escritura misma sean atómicas frente a otros hilos.
cerrojo = threading.Lock()


@dataclass
class EntradaDirectorio:
    nombre: str
    tamanio: int
    cluster_inicial: int
    fecha_creacion: datetime
    fecha_modificacion: datetime
    # Offset absoluto (en bytes) del inicio de la entrada de 64 bytes
    # dentro de la imagen. Lo necesito para modificar la entrada en el
    # borrado lógico sin volver a buscarla.
    offset_en_disco: int


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


def _parsear_entrada(bloque, offset_en_disco):
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
        offset_en_disco=offset_en_disco,
    )


def leer_directorio(ruta):
    """Devuelve las entradas activas (no libres) del directorio."""
    base = CLUSTER_INICIO_DIRECTORIO * TAMANIO_CLUSTER
    with open(ruta, 'rb') as f:
        f.seek(base)
        crudo = f.read(NUM_CLUSTERS_DIRECTORIO * TAMANIO_CLUSTER)

    entradas = []
    for i in range(len(crudo) // TAMANIO_ENTRADA):
        bloque = crudo[i * TAMANIO_ENTRADA:(i + 1) * TAMANIO_ENTRADA]
        if _es_entrada_libre(bloque):
            continue
        entradas.append(_parsear_entrada(bloque, base + i * TAMANIO_ENTRADA))
    return entradas


def _clusters_necesarios(tamanio):
    return math.ceil(tamanio / TAMANIO_CLUSTER)


def _clusters_ocupados(entradas):
    ocup = set()
    for e in entradas:
        for c in range(e.cluster_inicial,
                       e.cluster_inicial + _clusters_necesarios(e.tamanio)):
            ocup.add(c)
    return ocup


def _primer_hueco_contiguo(entradas, clusters):
    """First-fit sobre el área de datos."""
    ocup = _clusters_ocupados(entradas)
    inicio = CLUSTER_INICIO_DATOS
    libres = 0
    for c in range(CLUSTER_INICIO_DATOS, TOTAL_CLUSTERS):
        if c in ocup:
            inicio = c + 1
            libres = 0
        else:
            libres += 1
            if libres >= clusters:
                return inicio
    raise ValueError(
        f'No hay {clusters} clúster(es) contiguos libres en el área de datos.'
    )


def _offset_primera_entrada_libre(ruta):
    base = CLUSTER_INICIO_DIRECTORIO * TAMANIO_CLUSTER
    with open(ruta, 'rb') as f:
        f.seek(base)
        crudo = f.read(NUM_CLUSTERS_DIRECTORIO * TAMANIO_CLUSTER)
    for i in range(len(crudo) // TAMANIO_ENTRADA):
        bloque = crudo[i * TAMANIO_ENTRADA:(i + 1) * TAMANIO_ENTRADA]
        if _es_entrada_libre(bloque):
            return base + i * TAMANIO_ENTRADA
    raise ValueError('El directorio está lleno; no hay entradas libres.')


def insertar(ruta, ruta_local):
    if not os.path.isfile(ruta_local):
        raise FileNotFoundError(f'No existe el archivo local «{ruta_local}».')

    nombre = os.path.basename(ruta_local)
    if len(nombre) > LONGITUD_NOMBRE:
        raise ValueError(
            f'El nombre «{nombre}» excede {LONGITUD_NOMBRE} caracteres.'
        )
    if not all(ord(c) < 128 for c in nombre):
        raise ValueError('El nombre contiene caracteres fuera de ASCII de 7 bits.')

    with open(ruta_local, 'rb') as f:
        contenido = f.read()
    tamanio = len(contenido)
    if tamanio == 0:
        raise ValueError('No se admite insertar un archivo vacío.')

    with cerrojo:
        entradas = leer_directorio(ruta)
        if any(e.nombre == nombre for e in entradas):
            raise ValueError(f'Ya existe «{nombre}» dentro de FiUnamFS.')

        n_clusters = _clusters_necesarios(tamanio)
        cluster_inicial = _primer_hueco_contiguo(entradas, n_clusters)
        offset_entrada = _offset_primera_entrada_libre(ruta)

        sello = datetime.now().strftime('%Y%m%d%H%M%S').encode('ascii')

        with open(ruta, 'r+b') as imagen:
            imagen.seek(cluster_inicial * TAMANIO_CLUSTER)
            imagen.write(contenido)

            # Rellenar el último clúster con ceros: evita exponer residuos
            # de un archivo previo si el espacio se reutilizó tras un borrado.
            residuo = tamanio % TAMANIO_CLUSTER
            if residuo:
                imagen.write(b'\x00' * (TAMANIO_CLUSTER - residuo))

            registro = bytearray(TAMANIO_ENTRADA)
            registro[OFFSET_TIPO:OFFSET_TIPO + 1] = TIPO_ARCHIVO
            nombre_bytes = nombre.encode('ascii').ljust(LONGITUD_NOMBRE, b' ')
            registro[OFFSET_NOMBRE:OFFSET_NOMBRE + LONGITUD_NOMBRE] = nombre_bytes
            struct.pack_into('<I', registro, OFFSET_TAMANIO, tamanio)
            struct.pack_into('<I', registro, OFFSET_CLUSTER_INICIAL, cluster_inicial)
            registro[OFFSET_FECHA_CREACION:OFFSET_FECHA_CREACION + LONGITUD_FECHA] = sello
            registro[OFFSET_FECHA_MODIFICACION:OFFSET_FECHA_MODIFICACION + LONGITUD_FECHA] = sello

            imagen.seek(offset_entrada)
            imagen.write(registro)

    print(f'Insertado «{nombre}» en clúster {cluster_inicial} '
          f'({tamanio:,} bytes, {n_clusters} clúster(es)).')


def _buscar_entrada(entradas, nombre):
    for e in entradas:
        if e.nombre == nombre:
            return e
    raise ValueError(f'No existe «{nombre}» en FiUnamFS.')


def extraer(ruta, nombre, destino):
    with cerrojo:
        entradas = leer_directorio(ruta)
        entrada = _buscar_entrada(entradas, nombre)
        with open(ruta, 'rb') as imagen:
            imagen.seek(entrada.cluster_inicial * TAMANIO_CLUSTER)
            contenido = imagen.read(entrada.tamanio)
    with open(destino, 'wb') as salida:
        salida.write(contenido)
    print(f'Extraído «{nombre}» → «{destino}» ({entrada.tamanio:,} bytes).')


def eliminar(ruta, nombre):
    """Borrado lógico: invalida la entrada sin tocar el área de datos."""
    with cerrojo:
        entradas = leer_directorio(ruta)
        entrada = _buscar_entrada(entradas, nombre)
        nombre_invalido = bytes([RELLENO_NOMBRE_LIBRE] * LONGITUD_NOMBRE)
        with open(ruta, 'r+b') as imagen:
            imagen.seek(entrada.offset_en_disco + OFFSET_TIPO)
            imagen.write(TIPO_ENTRADA_LIBRE)
            imagen.seek(entrada.offset_en_disco + OFFSET_NOMBRE)
            imagen.write(nombre_invalido)
    print(f'Eliminado «{nombre}».')


def listar(ruta):
    with cerrojo:
        entradas = leer_directorio(ruta)
    if not entradas:
        print('(El directorio está vacío.)')
        return

    print(f'{"Nombre":<16} {"Tamaño":>10} {"Clúster":>8}  '
          f'{"Creación":<19}  {"Modificación":<19}')
    print('-' * 80)
    for e in entradas:
        crea = (e.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S')
                if e.fecha_creacion else '—')
        modif = (e.fecha_modificacion.strftime('%Y-%m-%d %H:%M:%S')
                 if e.fecha_modificacion else '—')
        print(f'{e.nombre:<16} {e.tamanio:>10,} {e.cluster_inicial:>8}  '
              f'{crea:<19}  {modif:<19}')
    print('-' * 80)
    print(f'Total: {len(entradas)} archivo(s)')


def _ejecutar_en_hilo(funcion, *args):
    """Lanza la operación en un hilo y propaga cualquier excepción al main."""
    contenedor = {}

    def envoltura():
        try:
            funcion(*args)
        except Exception as err:
            contenedor['error'] = err

    hilo = threading.Thread(target=envoltura)
    hilo.start()
    hilo.join()
    if 'error' in contenedor:
        raise contenedor['error']


def _construir_parser():
    parser = argparse.ArgumentParser(
        prog='proyecto.py',
        description='Herramienta para manipular imágenes FiUnamFS (versión 26-2).',
    )
    parser.add_argument('imagen', help='Ruta a la imagen FiUnamFS (1440 KB).')
    sub = parser.add_subparsers(dest='comando', required=True)

    sub.add_parser('listar', help='Lista el contenido del directorio.')

    p_ext = sub.add_parser('extraer', help='Copia un archivo al equipo local.')
    p_ext.add_argument('nombre', help='Nombre del archivo dentro de FiUnamFS.')
    p_ext.add_argument('destino', help='Ruta local destino.')

    p_ins = sub.add_parser('insertar', help='Copia un archivo local a FiUnamFS.')
    p_ins.add_argument('ruta_local', help='Archivo local a insertar.')

    p_del = sub.add_parser('eliminar', help='Borrado lógico de un archivo.')
    p_del.add_argument('nombre', help='Nombre del archivo a eliminar.')

    return parser


def main():
    args = _construir_parser().parse_args()

    try:
        validar_imagen(args.imagen)
        if args.comando == 'listar':
            _ejecutar_en_hilo(listar, args.imagen)
        elif args.comando == 'extraer':
            _ejecutar_en_hilo(extraer, args.imagen, args.nombre, args.destino)
        elif args.comando == 'insertar':
            _ejecutar_en_hilo(insertar, args.imagen, args.ruta_local)
        elif args.comando == 'eliminar':
            _ejecutar_en_hilo(eliminar, args.imagen, args.nombre)
    except (FileNotFoundError, ValueError) as err:
        print(f'Error: {err}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
