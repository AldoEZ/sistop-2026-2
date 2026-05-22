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
- `filesystem.py`: funciones y métodos
- `fiunamfs.img`: imagen de prueba

## Cómo ejecutar

1. Abrir una terminal en esta carpeta.
2. Ejecutar:
   - `python3 main.py`

Si el archivo `fiunamfs.img` existe en la misma carpeta, el programa lo abrirá y validará.

Sugerencia en Linux:
- Verifica que está en la carpeta: `ls -l`
- Ejecuta: `python3 main.py`

## Funcionalidad implementada (commit actual)

**Listar archivos**

- Se valida el superbloque (nombre `FiUnamFS` y versión `26-2`).
- Se recorre el directorio (entradas de 64 bytes) y se imprimen los archivos existentes.

## Sincronización / Concurrencia

- El menú crea un **hilo** para ejecutar la operación seleccionada.
- En `filesystem.py` se usa un **`Lock`** para proteger el acceso a la imagen cuando se lee el directorio.
- El hilo se sincroniza con el principal mediante `join()`.

## Notas

- Los campos numéricos del directorio están en **little endian** (`struct.unpack('<I', ...)`).
- El directorio comienza en el offset 2048 (cluster 1) con 256 entradas de 64 bytes.
