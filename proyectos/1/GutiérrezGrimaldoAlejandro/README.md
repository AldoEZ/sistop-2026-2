# FiUnamFS

Programa para leer y modificar imágenes del sistema de archivos FiUnamFS (versión 26-2).

## Autor

- Alejandro Gutiérrez Grimaldo

## Requisitos

- Node.js >= 16

No se requiere instalar dependencias externas (`npm install` no es necesario).

## Uso desde línea de comandos

Desde el directorio del proyecto (`proyectos/1/GutiérrezGrimaldoAlejandro/`):

```bash
node index.js listar  <imagen.img>
node index.js copiar  <imagen.img> <nombre> <destino>
node index.js agregar <imagen.img> <archivo_local> [nombre]
node index.js eliminar <imagen.img> <nombre>
```

### Ejemplos

```bash
node index.js listar   ../fiunamfs.img
node index.js copiar   ../fiunamfs.img README.org /tmp/README.org
node index.js agregar  ../fiunamfs.img /tmp/foto.png foto.png
node index.js eliminar ../fiunamfs.img foto.png
```

> La imagen de ejemplo `fiunamfs.img` está en `proyectos/1/`.

## Interfaz web

```bash
node server.js ../fiunamfs.img
# abrir http://localhost:8080
```

También se puede indicar otro puerto:

```bash
node server.js ../fiunamfs.img 3000
```

## Capturas

### Listado del directorio (CLI)

![cli-listar](img/cli-listar.png)

### Interfaz web

![web](img/web.png)

## Estructura

```
fiunamfs.js  - logica del sistema de archivos (superbloque, directorio, lectura y escritura)
worker.js    - hilo de trabajo con worker_threads
index.js     - CLI
server.js    - servidor web con interfaz grafica
```

## Concurrencia

Cada operación se ejecuta en un worker separado usando `worker_threads`. El hilo principal manda la operación con `workerData` y espera la respuesta como una Promise. De esta forma el hilo principal nunca se bloquea mientras el worker lee o escribe sobre la imagen.
