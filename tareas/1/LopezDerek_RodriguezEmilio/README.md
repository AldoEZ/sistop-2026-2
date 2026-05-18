# Práctica 1 – Minishell en Python

## Descripción

En esta práctica se desarrolló un pequeño programa en Python que funciona como una **mini shell**, es decir, una interfaz sencilla desde la cual el usuario puede ejecutar comandos del sistema operativo desde la terminal.

El programa muestra un prompt (`minishell>`) donde el usuario puede escribir comandos como `ls`, `pwd`, `echo`, entre otros. Cuando se introduce un comando, el programa crea un **proceso hijo** utilizando la llamada al sistema `fork()`. Después, ese proceso hijo reemplaza su ejecución usando `execvp()` para ejecutar el comando solicitado.

También se implementó el manejo de la señal **SIGCHLD**, que permite detectar cuando un proceso hijo termina su ejecución. Para evitar que queden procesos zombie, se utiliza `waitpid()` con la opción `WNOHANG`, lo que permite recolectar los procesos hijos sin bloquear el programa.

---

## Instrucciones de ejecución

Para ejecutar el programa es necesario contar con un sistema Linux o un entorno compatible. En este caso se utilizó **WSL (Windows Subsystem for Linux)** para poder ejecutar las llamadas al sistema necesarias.

1. Abrir una terminal.
2. Ubicarse en la carpeta donde se encuentra el archivo `minishell.py`.

```bash
cd ruta/de/la/carpeta
```

3. Ejecutar el programa con Python:

```bash
python3 minishell.py
```

Después de ejecutarlo aparecerá el prompt:

```
minishell>
```

Desde ahí se pueden introducir comandos del sistema.

Para salir del programa se puede escribir:

```
exit
```

---

## Explicación general del diseño

El programa se organizó en varias funciones para separar las diferentes tareas.

La función **setup_signals()** se encarga de configurar el manejo de señales del programa. En particular, se instala un manejador para `SIGCHLD`, que se activa cuando termina un proceso hijo.

La función **sigchld_handler()** se ejecuta cuando llega esa señal y utiliza `waitpid()` para recolectar los procesos hijos que ya terminaron.

La función **execute_command()** es la que crea un proceso hijo mediante `fork()`. El proceso hijo ejecuta el comando introducido usando `execvp()`, mientras que el proceso padre continúa esperando nuevos comandos.

Finalmente, la función **main()** contiene el ciclo principal del programa, donde se lee lo que escribe el usuario, se procesan los argumentos del comando y se llama a la función que lo ejecuta.

---

## Ejemplo de ejecución

```
minishell> ls
minishell.py
[Proceso hijo 604 terminado]

minishell> pwd
/mnt/c/Users/Usuario/sistop-2026-2/tareas/1

minishell> echo Hola
Hola
[Proceso hijo 615 terminado]

minishell> sleep 2
[Proceso hijo 620 terminado]

minishell> exit
Saliendo de minishell...
```

---

## Dificultades encontradas

Una de las principales dificultades fue que el programa no funcionaba directamente en Windows, ya que funciones como `fork()` y el manejo de señales (`SIGCHLD`) no están disponibles en este sistema.

Para solucionarlo se utilizó **WSL**, lo que permitió ejecutar el programa dentro de un entorno Linux desde la misma computadora.

Otra dificultad fue entender cómo funcionan `fork()` y `execvp()`, ya que el primero crea una copia del proceso actual y el segundo reemplaza el proceso hijo por el programa que se desea ejecutar. Una vez entendido ese flujo, fue más claro cómo implementar la ejecución de comandos.

---

## Comentario final

Esta práctica ayudó a entender mejor cómo funcionan los procesos en sistemas tipo Unix, especialmente la creación de procesos hijos y la ejecución de programas mediante llamadas al sistema. También permitió ver de forma práctica cómo las shells utilizan estos mecanismos para ejecutar comandos introducidos por el usuario.

