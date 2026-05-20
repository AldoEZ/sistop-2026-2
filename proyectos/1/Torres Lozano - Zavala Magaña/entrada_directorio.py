# entrada_directorio.py
# Módulo que representa una entrada del directorio de FiUnamFS.
# Ya implementamos la lectura de contenido desde el .img.
# Todavía falta terminar la copia al sistema local.

import os
import math
import struct

# Un cluster = 4 sectores × 512 bytes = 2048 bytes
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

    def clusters_used(self) -> tuple[int, list[int]]:
        """
        Devuelve cuántos clusters ocupa el archivo y cuáles son.
        FiUnamFS usa asignación contigua, así que siempre son consecutivos.
        """
        # Nota: Esto ya está bin. Como el FS es de asignación contigua 
        # no necesitamos FAT. Con esto ya sabemos dónde leer
        cantidad = math.ceil(self.size / TAMANO_CLUSTER)
        lista_clusters = list(range(self.initial_cluster, self.initial_cluster + cantidad))
        return cantidad, lista_clusters

    def _leer_contenido(self) -> bytes | None:
        """Lee los bytes del archivo desde la imagen .img."""
        # Quedó bien la lectura del archivo desde el .img. 
        # nos evitamos cargar clusters vacíos, leyendo solo self.size
        desplazamiento = self.initial_cluster * TAMANO_CLUSTER
        try:
            with open(self.img_path, "rb") as img:
                img.seek(desplazamiento)
                return img.read(self.size)
        except OSError:
            return None

    def copy_to_system(self, directorio_destino: str) -> bool:
        # Zavala terminar de implementar la copia al sistema local
        # Aquí literal solo tenemos que mandar llamar self._leer_contenido,
        # armar la ruta con os.path.join (directorio_destino, self.name) 
        return False

    @staticmethod
    def _formatear_fecha(crudo: str) -> str:
        """
        Convierte la fecha compacta del FS a formato legible.
        Ejemplo: '20260108182600' → '2026-01-08 18:26:00'
        """
        if len(crudo) < 14:
            return "Fecha inválida"
        return (
            f"{crudo[0:4]}-{crudo[4:6]}-{crudo[6:8]} "
            f"{crudo[8:10]}:{crudo[10:12]}:{crudo[12:14]}"
        )
