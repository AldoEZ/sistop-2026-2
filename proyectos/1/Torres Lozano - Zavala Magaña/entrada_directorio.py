# entrada_directorio.py
# Módulo que representará una entrada del directorio de FiUnamFS.
# Por ahora solo definimos la clase con sus atributos básicos.
# Todavía falta implementar la copia y el cálculo de clusters.

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
        """Calcula cuántos clusters ocupa el archivo y cuáles son."""
        # Acuérdate que el sistema es de "asignación contigua". 
        # Esta lógica ya asume que están pegados, está bien según la especificación.
        # No lo muevas, esto ya sirve para calcular el espacio.
        cantidad = math.ceil(self.size / TAMANO_CLUSTER)
        lista_clusters = list(range(self.initial_cluster, self.initial_cluster + cantidad))
        return cantidad, lista_clusters

    def _leer_contenido(self) -> bytes | None:
        # implementar lectura desde el .img
        # Tenemos que abrir self.img_path en modo "rb", movernos al offset
        # (self.initial_cluster * TAMANO_CLUSTER) y leer exactamente self.size bytes
        # para la función de copiar hacia la compu
        return None

    def copy_to_system(self, directorio_destino: str) -> bool:
        # hacer copia al sistema local
        # Aquí hay que llamar a self._leer_contenido() y guardar esos bytes
        # en un archivo nuevo dentro de directoriodestino.
        # manejar los hilos7semáforos aquí si lo hacemos concurrente.
        return False

    @staticmethod
    def _formatear_fecha(crudo: str) -> str:
        #El profe dice que el formato viene como AAAAMMDDHHMMSS. 
        # La limpieza que hiciste aquí ya está bien, solo hay que asegurar
        # que cuando leamos del directorio le pasemos este string tal cual.
        if len(crudo) < 14:
            return "Fecha inválida"
        return (
            f"{crudo[0:4]}-{crudo[4:6]}-{crudo[6:8]} "
            f"{crudo[8:10]}:{crudo[10:12]}:{crudo[12:14]}"
        )
