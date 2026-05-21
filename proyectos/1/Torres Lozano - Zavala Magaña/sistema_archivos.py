# sistema_archivos.py
# Ya tenemos funcionando el listado y la copia de archivos.
# Todavía falta implementar la eliminación de archivos.

import os
import math
import struct
import threading
from datetime import datetime

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
        """Copia un archivo desde FiUnamFS hacia un directorio en la computadora."""
        archivos = self.listar_archivos()
        for archivo in archivos:
            if archivo.name == nombre_archivo:
                if archivo.copy_to_system(directorio_destino):
                    return f'[OK] "{nombre_archivo}" copiado en "{directorio_destino}".'
                else:
                    return f'[Error] No se pudo copiar "{nombre_archivo}". Revisa que la ruta exista y el archivo no esté ya ahí.'
        return f'[Error] "{nombre_archivo}" no existe en FiUnamFS.'

    def copiar_desde_local(self, ruta_origen: str) -> str:
        """Copia un archivo desde la computadora hacia FiUnamFS."""
        if not os.path.exists(ruta_origen):
            return "[Error] El archivo no existe en esa ruta."

        nombre_archivo = os.path.basename(ruta_origen)

        if len(nombre_archivo) > 14:
            return f'[Error] El nombre "{nombre_archivo}" supera los 14 caracteres permitidos.'

        if not nombre_archivo.isascii():
            return f'[Error] El nombre "{nombre_archivo}" contiene caracteres no ASCII.'

        for archivo in self.listar_archivos():
            if archivo.name == nombre_archivo:
                return f'[Error] Ya existe un archivo llamado "{nombre_archivo}" en FiUnamFS.'

        tamano_archivo  = os.path.getsize(ruta_origen)
        cluster_inicial = self._buscar_espacio_libre(tamano_archivo)
        if cluster_inicial is None:
            return "[Error] No hay espacio contiguo suficiente en FiUnamFS."

        try:
            with open(ruta_origen, "rb") as origen:
                contenido = origen.read()
            desplazamiento = cluster_inicial * CLUSTER_SIZE
            with self._candado:
                with open(self.ruta, "rb+") as img:
                    img.seek(desplazamiento)
                    img.write(contenido)
        except OSError:
            return "[Error] Error al escribir los datos del archivo en la imagen."

        return self._escribir_entrada_directorio(ruta_origen, nombre_archivo, tamano_archivo, cluster_inicial)

    def eliminar_archivo(self, nombre_archivo: str) -> str:
        # implementar eliminación de archivos
        # Buscar la entrada del archivo en el directorio,
        # y marcarla con / para indicar que está libre.
        return "[Error] Eliminar archivos aún no está implementado."

    def _leer_cadena(self, offset: int, longitud: int) -> str:
        with open(self.ruta, "rb") as img:
            img.seek(offset)
            return img.read(longitud).decode("ascii").strip()

    def _leer_entero(self, offset: int, longitud: int) -> int:
        with open(self.ruta, "rb") as img:
            img.seek(offset)
            (valor,) = struct.unpack("<I", img.read(longitud))
            return valor

    def _leer_nombre_crudo(self, indice: int) -> str | None:
        desplazamiento = INICIO_DIR + (indice * TAMANO_ENTRADA)
        try:
            with open(self.ruta, "rb") as img:
                img.seek(desplazamiento)
                nombre_crudo = img.read(15).decode("ascii")
            if nombre_crudo[0] == ENTRADA_ARCHIVO:
                return nombre_crudo
            return None
        except (OSError, UnicodeDecodeError):
            return None

    def _leer_entrada(self, indice: int) -> FileEntry | None:
        """Lee una entrada completa del directorio y construye un FileEntry."""
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

    def _buscar_espacio_libre(self, tamano_archivo: int) -> int | None:
        """Busca clusters contiguos libres donde quepa el archivo."""
        clusters_necesarios = math.ceil(tamano_archivo / CLUSTER_SIZE)
        reservados = set(range(self.clusters_dir + 1))
        ocupados   = set()
        for archivo in self.listar_archivos():
            _, lista = archivo.clusters_used()
            ocupados.update(lista)
        libres = [
            c for c in range(self.total_clusters)
            if c not in reservados and c not in ocupados
        ]
        for i in range(len(libres) - clusters_necesarios + 1):
            if all(libres[i + j] == libres[i] + j for j in range(clusters_necesarios)):
                return libres[i]
        return None

    def _escribir_entrada_directorio(
        self, ruta_origen: str, nombre_archivo: str, tamano_archivo: int, cluster: int
    ) -> str:
        """Escribe los metadatos del nuevo archivo en la primera entrada libre."""
        for i in range(self.max_entradas):
            desplazamiento = INICIO_DIR + (i * TAMANO_ENTRADA)
            try:
                with open(self.ruta, "rb") as img:
                    img.seek(desplazamiento)
                    marcador = img.read(1).decode("ascii")
            except (OSError, UnicodeDecodeError):
                continue
            if marcador != ENTRADA_LIBRE:
                continue
            nombre_relleno      = ("-" + nombre_archivo).ljust(15).encode("ascii")
            tamano_empaquetado  = struct.pack("<I", tamano_archivo)
            cluster_empaquetado = struct.pack("<I", cluster)
            fecha_creacion      = datetime.fromtimestamp(
                os.path.getctime(ruta_origen)).strftime("%Y%m%d%H%M%S").encode("ascii")
            fecha_modificacion  = datetime.fromtimestamp(
                os.path.getmtime(ruta_origen)).strftime("%Y%m%d%H%M%S").encode("ascii")
            with self._candado:
                try:
                    with open(self.ruta, "rb+") as img:
                        img.seek(desplazamiento);      img.write(nombre_relleno)
                        img.seek(desplazamiento + 16); img.write(tamano_empaquetado)
                        img.seek(desplazamiento + 20); img.write(cluster_empaquetado)
                        img.seek(desplazamiento + 30); img.write(fecha_creacion)
                        img.seek(desplazamiento + 50); img.write(fecha_modificacion)
                    return f'[OK] "{nombre_archivo}" copiado a FiUnamFS exitosamente.'
                except OSError:
                    return "[Error] Error al escribir la entrada en el directorio."
        return "[Error] No hay entradas libres en el directorio de FiUnamFS."
