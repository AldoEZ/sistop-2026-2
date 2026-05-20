# sistema_archivos.py
# Ya tenemos funcionando la lectura del directorio con 8 hilos en paralelo.
# Todavía falta implementar copiar y eliminar archivos.

import os
import math
import struct
import threading

from entrada_directorio import FileEntry, CLUSTER_SIZE

NOMBRE_FS         = "FiUnamFS"
VERSIONES_VALIDAS = {"26-2", "24-2"}
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
        self._candado       = threading.Lock()
        self.nombre         = self._leer_cadena(OFFSET_NOMBRE, 8)
        self.version        = self._leer_cadena(OFFSET_VERSION, 4)
        self.etiqueta       = self._leer_cadena(OFFSET_ETIQUETA, 15)
        self.tam_cluster    = self._leer_entero(OFFSET_TAM_CLUSTER, 4)
        self.clusters_dir   = self._leer_entero(OFFSET_CLUSTERS_DIR, 4)
        self.total_clusters = self._leer_entero(OFFSET_TOTAL, 4)
        self.max_entradas   = (self.tam_cluster * self.clusters_dir) // TAMANO_ENTRADA

    def listar_archivos(self) -> list[FileEntry]:
        """
        Lee el directorio usando 8 hilos en paralelo.
        Cada hilo lee su fragmento y agrega los resultados a la lista compartida.
        Una barrera manual espera a que todos terminen.
        """
        # Luigi bien este pedazo, El uso del candado_resultados 
        # y la barrera manual con semaforo ya está. 
        # Solo no hay que olvidar usar self._candado (el del FS general) 
        # en las operaciones de escritura que haremos después.
        resultados: list[FileEntry] = []
        candado_resultados = threading.Lock()

        num_hilos = 8
        fragmento = self.max_entradas // num_hilos

        pendientes   = [num_hilos]
        barrera      = threading.Semaphore(0)
        candado_cont = threading.Lock()

        def trabajador(indice_inicio: int):
            local = []
            for i in range(indice_inicio, indice_inicio + fragmento):
                entrada = self._leer_entrada(i)
                if entrada is not None:
                    local.append(entrada)
            with candado_resultados:
                resultados.extend(local)
            with candado_cont:
                pendientes[0] -= 1
                if pendientes[0] == 0:
                    barrera.release()

        hilos = [
            threading.Thread(target=trabajador, args=(i * fragmento,))
            for i in range(num_hilos)
        ]
        for hilo in hilos:
            hilo.start()

        barrera.acquire()
        return resultados

    def copiar_a_local(self, nombre_archivo: str, directorio_destino: str) -> str:
        # Zavala falta
        # Buscar el archivo iterando sobre self.listar_archivos
        # Si lo encontramos, le damos .copy_to_system
        # Acuérdate de meter todo el bloque en un with self._candado
        return "[Error] Función aún no implementada."

    def copiar_desde_local(self, ruta_origen: str) -> str:
        # Luis 
        # Este es el monstruo final del proyecto. Necesitamos:
        # Leer tamaño del archivo local.
        # Buscar si hay suficientes clusters libres contiguos (hacer una funcioncita para eso).
        # Buscar un espacio libre en el directorio (/).
        # Escribir metadatos y datos (usar pack con <I de nuevo).
        return "[Error] Función aún no implementada."

    def eliminar_archivo(self, nombre_archivo: str) -> str:
        # buscar el archivo, calcular su offset en el disco
        return "[Error] Función aún no implementada."

    def _leer_cadena(self, offset: int, longitud: int) -> str:
        with open(self.ruta, "rb") as img:
            img.seek(offset)
            return img.read(longitud).decode("ascii").strip()

    def _leer_entero(self, offset: int, longitud: int) -> int:
        with open(self.ruta, "rb") as img:
            img.seek(offset)
            (valor,) = struct.unpack("<I", img.read(longitud))
            return valor

    def _leer_entrada(self, indice: int) -> FileEntry | None:
        """Lee una entrada completa del directorio y construye un FileEntry."""
        #
        desplazamiento = INICIO_DIR + (indice * TAMANO_ENTRADA)
        try:
            with open(self.ruta, "rb") as img:
                img.seek(desplazamiento)
                nombre_crudo = img.read(15).decode("ascii")
                if nombre_crudo[0] != ENTRADA_ARCHIVO:
                    return None
                img.seek(desplazamiento + 16)
                (tamano,) = struct.unpack("<I", img.read(4))
                img.seek(desplazamiento + 20)
                (cluster,) = struct.unpack("<I", img.read(4))
                img.seek(desplazamiento + 30)
                fecha_creacion = img.read(14).decode("ascii")
                img.seek(desplazamiento + 50)
                fecha_modificacion = img.read(14).decode("ascii")
            return FileEntry(
                name=nombre_crudo[1:].strip(),
                size=tamano,
                initial_cluster=cluster,
                creation_date=fecha_creacion,
                update_date=fecha_modificacion,
                img_path=self.ruta,
            )
        except (OSError, UnicodeDecodeError, struct.error):
            return None
