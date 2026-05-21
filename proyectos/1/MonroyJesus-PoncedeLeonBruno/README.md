# FiUnamFS — Micro sistema de archivos multihilo con FUSE

## Autores

- **Monroy Tapia Jesús Alejandro**
- **Ponce de León Reyes Bruno**

---

**Proyecto Sistemas Operativos — Facultad de Ingeniería, UNAM**
Implementación en C con FUSE (Filesystem in Userspace)

---

## Descripción

`fiunamfs` es un módulo FUSE que monta una imagen de disco que sigue la
especificación **FiUnamFS** (disco de 1 440 KiB, sectores de 512 bytes,
                             clusters de 4 sectores, directorio plano de 8 clusters).

Una vez montado, el sistema de archivos aparece como un directorio normal del
sistema anfitrión y puede operarse con comandos estándar como `ls`, `cp`, `rm`,
entre otros.

> **Versiones soportadas:** el código acepta cualquier imagen cuya versión
> coincida con la constante `FS_VERSION` definida en `fiunamfs.c`. Por omisión
> es `"26-2"`. Si la imagen entregada usa una versión distinta (por ejemplo
> `"24-2"`), ver la sección [Cambio de versión](#cambio-de-versión).


---

## Requisitos de uso


| Componente     | Versión mínima              |
| -------------- | ----------------------------- |
| GCC            | 11                            |
| libfuse3-dev   | 3.x                           |
| POSIX pthreads | (incluido en glibc)           |
| Linux kernel   | 5.x con módulo`fuse` cargado |


<br>

### Instalación de dependencias (Debian 13 Trixie / Ubuntu)

```bash
sudo apt update
sudo apt install git pkg-config make gcc libfuse3-dev

# Verificar que el módulo FUSE esté cargado en el kernel
lsmod | grep fuse

# Si no aparece, cargarlo manualmente
sudo modprobe fuse
```

---

## Compilación

```bash
make
```

Genera el ejecutable `./fiunamfs`. Para limpiar y recompilar desde cero:

```bash
make clean && make
```

---

## Explicación de uso

Se requiere el ejecutable `./fiunamfs` compilado y un archivo imagen `.img`.
La imagen actúa como disco virtual sobre el que el sistema de archivos opera.

```bash
# 1. Crear punto de montaje
mkdir -p mnt

# 2. Montar la imagen en primer plano (muestra mensajes de diagnóstico)
./fiunamfs fiunamfs.img mnt -f

# 3. En OTRA terminal, operar normalmente:

ls -lh mnt/                          # listar contenido
cp mnt/archivo.txt ~/copia.txt       # copiar DESDE FiUnamFS al sistema
cp ~/mi_archivo.txt mnt/destino.txt  # copiar DEL sistema HACIA FiUnamFS
rm mnt/archivo.txt                   # eliminar archivo del FiUnamFS

# 4. Desmontar (cierra el hilo sync y el descriptor de disco)
fusermount3 -u mnt
```

---

## Cambio de versión

La imagen de prueba puede tener una versión distinta a `"26-2"`. Al intentar
montarla el programa mostrará:

```
Error: Version '24-2' no soportada (Se requiere: '26-2')
```

**Paso 1 — Verificar la versión de la imagen** (sin modificar nada):

```bash
dd if=fiunamfs.img bs=1 skip=14 count=5 2>/dev/null
```

**Paso 2 — Ajustar la constante en `fiunamfs.c`**:

```c
// Cambiar esta línea con el valor que devolvió dd:
#define FS_VERSION  "24-2"
```

**Paso 3 — Recompilar**:

```bash
make clean && make
```

---

## Comportamiento conocido — relleno de espacios en nombres de archivo

Algunas imágenes FiUnamFS almacenan el campo `name` (15 bytes de ancho fijo)
rellenando con **espacios** (`0x20`) los bytes sobrantes en lugar de ceros.
Esto causa que `ls` muestre los nombres con espacios al final:

```
'logo.png      '    ← espacios de relleno visibles
'mensaje.jpg   '
```

y que `cp` falle porque el shell busca `logo.png` pero el nombre real
almacenado es `logo.png      `.

**Solución implementada** en `raw_to_entry()`: al cargar cada entrada del
directorio se recortan los espacios finales antes de exponer el nombre al
sistema operativo:

```c
for (int i = NAME_LEN - 1; i >= 0; i--) {
  if (e->name[i] == ' ' || e->name[i] == '\0') {
    e->name[i] = '\0';
  } else {
    break; 
  }
}
```

Con este fix los nombres se ven y se usan correctamente:

```
logo.png
mensaje.jpg
README.org
```

---

## Ejemplos de uso

### Listar el contenido del sistema de archivos

Este es el contenido original de la imagen 'fiunamfs.img'

```bash
$ ls -lh mnt/
total 0
-rw-r--r-- 1 root root 124K dic 31  1969 logo.png
-rw-r--r-- 1 root root 177K dic 31  1969 mensaje.jpg
-rw-r--r-- 1 root root  31K dic 31  1969 README.org
```

![Imagen del programa al listar](img/ejemploListarContenido.png)


> La fecha `dic 31 1969` aparece cuando el campo de timestamp en la imagen
> está vacío o en cero. Es normal y no afecta la funcionalidad.

### Copiar un archivo desde FiUnamFS hacia el sistema anfitrión

```bash
$ cp mnt/logo.png ~/logo_local.png
$ ls -lh ~/logo_local.png
-rw-r--r-- 1 usuario usuario 124K may 19 22:10 logo_local.png
```

![Imagen del programa al copiar](img/ejemploCopiar1.png)


### Copiar un archivo del sistema anfitrión hacia FiUnamFS

```bash
$ cp ~/documento.txt mnt/documento.txt
$ ls -lh mnt/documento.txt
-rw-r--r-- 1 root root 4.2K may 19 22:11 documento.txt
```

![Imagen del programa al copiar](img/ejemploCopiar2.png)

### Eliminar un archivo del FiUnamFS

```bash
$ ls -lh mnt/
-rw-r--r-- 1 root root 124K dic 31  1969 logo.png
-rw-r--r-- 1 root root 177K dic 31  1969 mensaje.jpg
-rw-r--r-- 1 root root  31K dic 31  1969 README.org

$ rm mnt/logo.png

$ ls -lh mnt/
-rw-r--r-- 1 root root 177K dic 31  1969 mensaje.jpg
-rw-r--r-- 1 root root  31K dic 31  1969 README.org
```

![Imagen del programa al eliminar](img/ejemploEliminar.png)


> La entrada en el directorio se marca con tipo `'/'` y nombre `###############`.
> El espacio en disco queda disponible para el siguiente archivo que se cree.

### Renombrar un archivo dentro del FiUnamFS

```bash
$ mv mnt/mensaje.jpg mnt/foto.jpg

$ ls -lh mnt/
-rw-r--r-- 1 root root 177K may 20 21:14 foto.jpg
-rw-r--r-- 1 root root  31K dic 31  1969 README.org
```

![Imagen del programa al renombrar](img/ejemploRenombrar.png)

### Ver el espacio disponible en disco

```bash
$ df -h mnt/
S.ficheros     Tamaño Usados  Disp Uso% Montado en
fiunamfs         1,4M    208K  1,2M  15% /home/usuario/Escritorio/mnt
```

![Ver espacio](img/ejemploEspacio.png)

### Verificar la versión de cualquier imagen sin montar

```bash
$ dd if=fiunamfs.img bs=1 skip=14 count=5 2>/dev/null
24-2
```

![Revisar versión](img/ejemploVersion.png)


### Desmontar de forma segura

```bash
$ fusermount3 -u mnt
# El proceso fiunamfs termina automáticamente,
# sync_thread persiste los cambios pendientes y cierra el descriptor.
```

---

## Estructura del proyecto

```
fiunamfs/
├── fiunamfs.c   — implementación (FUSE + lógica FS + sincronización de hilos)
├── fiunamfs.img - Imagen para la prueba del sistema de archivos FiUnamFS (disco virtual)
├── Makefile     — reglas de compilación
└── README.md    — este documento
```

---

## Arquitectura multihilo y sincronización de hilos

El programa emplea **dos hilos de ejecución** que se comunican mediante
mecanismos de sincronización POSIX (`pthread_mutex_t` y `pthread_cond_t`).

### Hilo 1 — Hilo FUSE (principal)

Gestiona las llamadas del kernel: `getattr`, `readdir`, `open`, `read`,
`write`, `create`, `truncate`, `unlink`, `rename`, etc.

Protege el acceso a `g_fs.dir[]` y al descriptor `g_fs.fd` con `fs_mutex`.

### Hilo 2 — Hilo de sincronización (`sync_thread`)

Corre en paralelo. Permanece bloqueado en `pthread_cond_wait` sobre
`sync_cond`, sin consumir CPU, hasta que el hilo FUSE modifica el directorio.

Cuando se crea, elimina o renombra un archivo, el hilo FUSE llama
`marcar_sucio()`: activa `dir_dirty = 1` y envía una señal sobre `sync_cond`.
El hilo sync despierta, toma `fs_mutex`, llama `volcar_directorio()` para
escribir los cambios al disco y vuelve a dormirse.

**Ventaja:** la latencia de escritura al disco queda desacoplada del camino
crítico del usuario. Las operaciones FUSE responden de inmediato; la
persistencia ocurre en segundo plano.

```
Hilo FUSE                           Hilo sync
─────────                           ──────────
modificar g_fs.dir[]
lock(sync_mutex)
dir_dirty = 1
signal(sync_cond) ────────────────▶ despierta de cond_wait
unlock(sync_mutex)                  lock(fs_mutex)
volcar_directorio()
unlock(fs_mutex)
dir_dirty = 0
vuelve a cond_wait
```

---

## Operaciones soportadas


| Operación POSIX   | Commit | Estado | Descripción                          |
|-------------------|--------|--------|--------------------------------------|
| `ls` / `readdir`  | 2      | ✅     | Lista el directorio raíz             |
| `stat`, `getattr` | 2      | ✅     | Atributos de archivos                |
| `open`            | 3      | ✅     | Apertura verificada                  |
| `cp mnt/f ~/dst`  | 3      | ✅     | Copia archivo **desde** FiUnamFS     |
| `cat`, `hexdump`  | 3      | ✅     | Lectura de contenido                 |
| `cp ~/src mnt/f`  | 4      | ✅     | Copia archivo **hacia** FiUnamFS     |
| `rm mnt/f`        | 5      | ✅     | Elimina archivo del FiUnamFS         |
| `mv mnt/a mnt/b`  | 5      | ✅     | Renombra archivo                     |
| `df -h mnt/`      | 5      | ✅     | Espacio disponible en el disco       |

---

## Notas

- Los nombres de archivo tienen un máximo de **15 caracteres** ASCII-7.
- El sistema de archivos usa **asignación contigua**: cada archivo ocupa
clusters consecutivos; no hay FAT ni inodos.
- Solo soporta un **directorio plano** (sin subdirectorios).
- La imagen debe medir exactamente **1 474 560 bytes** (1 440 KiB).
- Los timestamps en cero se muestran como `dic 31 1969` en `ls`; es
comportamiento normal de la época Unix y no afecta la funcionalidad.

---

## Referencias

- **Documentación oficial de FUSE 3** — libfuse project.
[https://libfuse.github.io/doxygen/](https://libfuse.github.io/doxygen/)
Referencia de la API: callbacks, `fuse_main`, `fuse_operations` y
`fuse_file_info`. Consultada para el diseño de `fiunamfs_read`,
`fiunamfs_create` y la tabla `fiunamfs_oper`.
- **Especificación del sistema de archivos FiUnamFS** — Gunnar Wolf,
Facultad de Ingeniería UNAM, 2026.
Fuente de las constantes de disco: offsets del superbloque, estructura
de entradas de directorio y formato de timestamps `AAAAMMDDHHMMSS`.
- **The Linux Programming Interface** — Michael Kerrisk, No Starch Press, 2010.
Capítulos 23 (hilos POSIX) y 30 (mutexes y variables de condición).
Base del patrón productor-consumidor en `sync_thread_func` / `marcar_sucio`.
[https://man7.org/tlpi/](https://man7.org/tlpi/)
- **pread(2) / pwrite(2)** — Linux man-pages.
[https://man7.org/linux/man-pages/man2/pread.2.html](https://man7.org/linux/man-pages/man2/pread.2.html)
Usadas en `leer_disco` y `escribir_disco` para acceso posicional
sin modificar el offset del descriptor de archivo.
- **Writing a Simple Filesystem Using FUSE in C** — FUSE Wiki, GitHub.
[https://github.com/libfuse/libfuse/wiki/Fuse-Tutorial](https://github.com/libfuse/libfuse/wiki/Fuse-Tutorial)
Guía práctica para la estructura de un módulo FUSE mínimo; sirvió de
base para la organización de `main()` y el reordenamiento de `argv`.
- **pthread_cond_wait(3)** — Linux man-pages.
[https://man7.org/linux/man-pages/man3/pthread_cond_wait.3p.html](https://man7.org/linux/man-pages/man3/pthread_cond_wait.3p.html)
Referencia del mecanismo de espera condicional utilizado en el hilo
de sincronización para evitar espera activa (*busy-waiting*).
