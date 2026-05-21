# entrada_directorio.py
# Ya está completo lectura, copia y cálculo de clusters funcionan.

import os
import math
import struct

TAMANO_CLUSTER = 2048
CLUSTER_SIZE = TAMANO_CLUSTER


class FileEntry:
    """
    Representa una entrada del directorio de FiUnamFS.
    Cada entrada ocupa 64 bytes y guarda los metadatos de un archivo.
    Los datos reales del archivo viven en los clusters de datos, no aquí.
    """

    def __init__(
        self,
        name: str,
        size: int,
        initial_cluster: int,
        creation_date: str,
        update_date: str,
        img_path: str,
    ) -> None:
        self.name            = name
        self.size            = size
        self.initial_cluster = initial_cluster
        self.creation_date   = self._formatear_fecha(creation_date)
        self.update_date     = self._formatear_fecha(update_date)
        self.img_path        = img_path

    def __str__(self) -> str:
        return self.name

    def copy_to_system(self, directorio_destino: str) -> bool:
        """
        Copia el archivo desde la imagen FiUnamFS hacia un directorio local.
        Retorna True si todo salió bien, False si algo falló.
        """
        ruta_destino = os.path.join(directorio_destino, self.name)

        if os.path.exists(ruta_destino):
            return False

        contenido = self._leer_contenido()
        if contenido is None:
            return False

        try:
            with open(ruta_destino, "wb") as archivo_nuevo:
                archivo_nuevo.write(contenido)
            return True
        except OSError:
            return False

    def clusters_used(self) -> tuple[int, list[int]]:
        """Devuelve cuántos clusters ocupa el archivo y cuáles son."""
        cantidad = math.ceil(self.size / TAMANO_CLUSTER)
        lista_clusters = list(range(self.initial_cluster, self.initial_cluster + cantidad))
        return cantidad, lista_clusters

    def _leer_contenido(self) -> bytes | None:
        """Lee los bytes del archivo directamente desde la imagen .img."""
        desplazamiento = self.initial_cluster * TAMANO_CLUSTER
        try:
            with open(self.img_path, "rb") as img:
                img.seek(desplazamiento)
                return img.read(self.size)
        except OSError:
            return None

    @staticmethod
    def _formatear_fecha(crudo: str) -> str:
        if len(crudo) < 14:
            return "Fecha inválida"
        return (
            f"{crudo[0:4]}-{crudo[4:6]}-{crudo[6:8]} "
            f"{crudo[8:10]}:{crudo[10:12]}:{crudo[12:14]}"
        )
