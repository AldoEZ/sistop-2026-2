# FiUnamFS — Micro sistema de archivos multihilo con FUSE

## Autores
- **Monroy Tapia Jesús Alejandro**
- **Ponce de León Reyes Bruno**

Proyecto Sistemas Operativos — Facultad de Ingeniería, UNAM  
Implementación en C con FUSE (Filesystem in Userspace)

---

## Descripción

`fiunamfs` es un módulo FUSE que monta una imagen de disco que sigue la
especificación **FiUnamFS v26-2** (disco de 1 440 KiB, sectores de 512 bytes,
clusters de 4 sectores, directorio plano de 8 clusters).

Una vez montado, el sistema de archivos aparece como un directorio normal del
sistema anfitrión y puede operarse con comandos para la gestión y manipulación de archivos y directorios como `ls`, `cp`, `rm`, entre otros.

---

## Requisitos de uso

| Componente        | Versión mínima |
|-------------------|----------------|
| GCC               | 11             |
| libfuse3-dev      | 3.x            |
| POSIX pthreads    | (incluido en glibc) |
| Linux kernel      | 5.x con módulo `fuse` cargado |

### Instalación de dependencias (Ubuntu / Debian)

Actualizar la lista local de paquetes e instalar la biblioteca de desarrollo de FUSE para compilar:

```bash
sudo apt update
sudo apt install pkg-config make gcc libfuse3-dev
```

---

## Compilación

Se debe de utilizar el Makefile para la compilación del proyecto, se puede emplear el siguiente comando para generar el ejecutable `./fiunamfs`

```bash
make
```

---

## Explicación de uso

Antes de utilizar el sistema de archivos se requiere del ejecutable `./fiunamfs` previamente compilado y de un archivo imagen `.img` sobre el cual se va a trabajar, para este proyecto se utilizó el que se nos fué brindado para realizar pruebas: `fiunamfs.img`.
El archivo imagen `.img` se utilizará como un disco virtual para poner a prueba el sistema de archivos FiUnamFS, aplicando sobre este los cambios producidos.

El archivo `fiunamfs.img` utiliza un sistema versión **"24-2"** por lo que se debe cambiar el valor de la constante `FS_VERSION` para aceptar el uso de esta imagen para las pruebas. Se regresa el valor a **"26-2"** si se va a emplear una imagen diseñada para esta versión.

A continuación se muestran los comandos necesarios para el montaje y uso del sistema de archivos:

```bash
# 1. Crear punto de montaje
mkdir -p mnt

# 2. Montar la imagen (en primer plano para ver mensajes)
./fiunamfs fiunamfs.img mnt -f

# 3. **En otra terminal**, operar normalmente dentro del punto de montaje:

# Comandos:
# Listar contenidos
ls -lh mnt/

# Copiar archivo del FiUnamFS hacia el sistema anfitrión (los picoparéntesis indican la zona en donde colocar el nombre del archivo, eliminarlos en la práctica)
cp mnt/<archivo.txt> ./<archivo_local.txt>

# Copiar archivo del sistema anfitrión hacia el FiUnamFS
cp ./<mi_archivo.txt> mnt/<mi_archivo.txt>

# Eliminar un archivo del FiUnamFS
rm mnt/<archivo.txt>

# 4. Desmontar y cerrar hilos y archivo de imagen
fusermount3 -u mnt
```

---

## Estructura del proyecto

El proyecto se compone por tres archivos principales:
1. Archivo en lenguaje C que implementa la lógica y todo el funcionamiento del sistema de archivos ***FiUnamFS***.
2. Archivo que permite la automatización de compilación del proyecto, se encarga de gestionar dependencias, realiza el enlazado con bibliotecas y recompilar archivos modificados.
3. Documentación del proyecto; se incluye la explicación de funcionamiento, instrucciones de uso, estructura y ejemplos de uso.

```
fiunamfs/
├── fiunamfs.c   — implementación completa (FUSE + lógica FS + sync)
├── Makefile     — reglas de compilación
└── README.md    — este documento (Documentación del proyecto)
```

---

## Arquitectura multihilo y sincronización de hilos

El programa usa **dos hilos de ejecución** que se comunican mediante
mecanismos de sincronización POSIX:

### Hilo 1 — Hilo FUSE (principal)
Este hilo se encarga de gestionar las llamadas del kernel: `getattr`, `readdir`, `read`, `write`,
`create`, `unlink`, `rename`, etc.  
Protege el acceso al directorio en memoria y al descriptor de disco con el
mutex `fs_mutex`.

### Hilo 2 — Hilo de sincronización (`sync_thread`)
Corre en paralelo. Espera bloqueado en la **variable de condición** `sync_cond`.
Cuando el hilo FUSE modifica el directorio (crea, elimina o renombra un
archivo), activa la bandera `dir_dirty` y señala `sync_cond`.
Una vez que se recibe la señal el hilo de sincronización despierta, toma `fs_mutex`, escribe el directorio completo al disco y vuelve a dormirse.

**Ventaja**: La latencia de persistencia en disco queda desacoplada del
camino crítico de las operaciones del usuario.

```
Hilo FUSE                          Hilo sync
─────────                          ──────────
modificar dir[] ──[lock sync_mutex]──▶ dir_dirty = 1
                ──[signal sync_cond]──▶ despierta
                                        lock fs_mutex
                                        flush_directory()
                                        unlock fs_mutex
                                        vuelve a esperar
```

---

## Operaciones soportadas

| Operación POSIX | Descripción |
|-----------------|-------------|
| `ls` / `readdir` | Lista el directorio raíz |
| `cp src mnt/dst` | Copia archivo hacia FiUnamFS |
| `cp mnt/src dst` | Copia archivo desde FiUnamFS |
| `rm mnt/file`    | Elimina archivo del FiUnamFS |
| `mv mnt/a mnt/b` | Renombra archivo dentro del FiUnamFS |
| `cat`, `stat`, etc. | Acceso de solo lectura general |


---

## Ejemplos de uso




---


## Notas

- Los nombres de archivo tienen un máximo de **15 caracteres** ASCII-7.
- El sistema de archivos es de **asignación contigua**: cada archivo ocupa
  clusters consecutivos; no hay FAT ni inodos.
- Solo soporta un **directorio plano** (sin subdirectorios).
- La imagen debe ser de exactamente **1 474 560 bytes** (1 440 KiB).
