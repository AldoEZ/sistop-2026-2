# Proyecto: (Micro) sistema de archivos multihilos - FiUnamFS (26-2)

## Autores

- Ortega Ayala Fernando
- López Granados Derek André

## Entorno y dependencias

- **Sistema operativo**: Linux
- **Lenguaje**: Python 3.x
- **Dependencias externas**: Ninguna
- **Módulos estándar usados**: `struct`, `threading`

## Estructura del proyecto

- `main.py`: menú e interacción con el usuario.
- `filesystem.py`: funciones y métodos.
- `fiunamfs.img`: imagen de prueba.

## Cómo ejecutar

1. Abrir una terminal en esta carpeta.
2. Ejecutar:
   - `python3 main.py`

Si el archivo `fiunamfs.img` existe en la misma carpeta, el programa lo abrirá y validará.

Sugerencia en Linux:

- Verifica que la imagen está en la carpeta: `ls -l`
- Ejecuta: `python3 main.py`

## Funcionalidad implementada (commit actual)

- **Listar archivos**: Se valida el superbloque (nombre `FiUnamFS` y versión `26-2`). Se recorre el directorio (entradas de 64 bytes) y se imprimen los archivos existentes validando que el tipo de archivo sea `-`.
- **Copiar desde FiUnamFS**: Se busca una entrada válida en el directorio por su nombre. Al encontrarla, se lee su tamaño y cluster inicial (`offset = cluster * 2048`). Se leen los bytes correspondientes de la sección de datos y se escriben en un archivo local en el sistema anfitrión.

## Sincronización / Concurrencia

- El menú crea un **hilo** (`threading.Thread`) para ejecutar la operación seleccionada sin bloquear el flujo principal de opciones.
- En `filesystem.py` se usa un **`Lock`** (`threading.Lock()`) para proteger el acceso de lectura y escritura a la imagen del sistema de archivos, asegurando la integridad de los datos.
- El hilo se sincroniza con el principal mediante `join()`.

## Notas

- Los campos numéricos del disco, como el tamaño y los clusters, están codificados en **little endian** de 32 bits y se decodifican usando `struct.unpack('<I', ...)`.
- El directorio comienza en el offset 2048 (cluster 1) con 256 entradas fijas de 64 bytes.
- Los clusters de datos están ubicados en un esquema de asignación contigua a partir del cluster 9.
