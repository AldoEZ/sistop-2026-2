# sistema_archivos.py
# Núcleo del programa. Por ahora solo lee el superbloque
# para verificar que el .img sea válido y obtener sus parámetros.
# Todavía falta implementar listar, copiar y eliminar archivos.

import os
import struct
import threading

from entrada_directorio import FileEntry, CLUSTER_SIZE

NOMBRE_FS         = "FiUnamFS"
VERSIONES_VALIDAS = {"26-2", "24-2"} # El profe solo pide validar la 26-2, igual y quitamos la 24-2 para asegurar el 100%.
TAMANO_ENTRADA    = 64
INICIO_DIR        = CLUSTER_SIZE

OFFSET_NOMBRE       = 5
OFFSET_VERSION      = 14
OFFSET_ETIQUETA     = 20
OFFSET_TAM_CLUSTER  = 40
OFFSET_CLUSTERS_DIR = 50
OFFSET_TOTAL        = 60

ENTRADA_ARCHIVO = "-"
ENTRADA_LIBRE   = "/"


def validar_imagen(ruta: str) -> bool:
    """Verifica que el .img sea un FiUnamFS válido."""
    try:
        with open(ruta, "rb") as img:
            img.seek(OFFSET_NOMBRE)
            nombre = img.read(8).decode("ascii").strip()
            if nombre != NOMBRE_FS:
                return False
            img.seek(OFFSET_VERSION)
            version = img.read(4).decode("ascii").strip()
            return version in VERSIONES_VALIDAS
    except (OSError, UnicodeDecodeError):
        return False


class FiUnamFS:
    """Clase principal para interactuar con una imagen FiUnamFS."""

    def __init__(self, ruta: str) -> None:
        self.ruta           = ruta
        # Ya pusiste el candado aquí, esta bien
        # Hay que usar with self_candado en los métodos de listar, copiar y borrar
        # para cumplir con la sincronización que pide el profe.
        self._candado       = threading.Lock()
        self.nombre         = self._leer_cadena(OFFSET_NOMBRE, 8)
        self.version        = self._leer_cadena(OFFSET_VERSION, 4)
        self.etiqueta       = self._leer_cadena(OFFSET_ETIQUETA, 15)
        self.tam_cluster    = self._leer_entero(OFFSET_TAM_CLUSTER, 4)
        self.clusters_dir   = self._leer_entero(OFFSET_CLUSTERS_DIR, 4)
        self.total_clusters = self._leer_entero(OFFSET_TOTAL, 4)
        self.max_entradas   = (self.tam_cluster * self.clusters_dir) // TAMANO_ENTRADA

    def listar_archivos(self) -> list[FileEntry]:
        # falta lectura del directorio con hilos
        # NOTA DE LA ESPECIFICACIÓN:
        # Hay que ir al cluster 1 (byte 2048).
        # Leer bloques de 64 bytes.
        # Si el byte 0 es -, es un archivo. Si es /, está libre.
        # Los offsets
        # 1-15: Nombre (ascii strip)
        # 16-20: Tamaño en bytes (struct.unpack('<I', data[16:20]))
        # 20-24: Cluster inicial (struct.unpack('<I', data[20:24]))
        # 30-44: Fecha creación (cadena ascii) -> Ojo con esto que el profe dijo que los corrigió en el doc, hacer pruebas con la imagen de muestra.
        # 50-64: Fecha modificación (cadena ascii)
        return []

    def copiar_a_local(self, nombre_archivo: str, directorio_destino: str) -> str:
        # falta
        # Buscar el nombre en el directorio
        # .Instanciar FileEntry y llamar a copy_to_system.
        # No olvides usar el self_candado
        return "Pendiente."

    def copiar_desde_local(self, ruta_origen: str) -> str:
        # falta
        # Esto va a estar más pesado:
        # Revisar tamaño de ruta_origen.
        # Buscar si hay suficientes clusters de datos contiguos libres (asignación contigua).
        # Buscar una entrada vacía en el directorio ('/' o nombre "###############").
        # Escribir metadatos y luego los bytes al disco.
        return "Pendiente"

    def eliminar_archivo(self, nombre_archivo: str) -> str:
        # falta
        # Aquí solo tenemos que buscar la entrada del archivo en el directorio, 
        # y sobreescribir el primer byte (0) con un / o cambiar el nombre a ###############.
        # Como no hay FAT ni nada, con eso ya se libera el espacio. Borrado.
        return "Pendiente"

    def _leer_cadena(self, offset: int, longitud: int) -> str:
        with open(self.ruta, "rb") as img:
            img.seek(offset)
            return img.read(longitud).decode("ascii").strip()

    def _leer_entero(self, offset: int, longitud: int) -> int:
        with open(self.ruta, "rb") as img:
            img.seek(offset)
            (valor,) = struct.unpack("<I", img.read(longitud))
            return valor
