# Tarea 01: Mini Shell
**Fecha de entrega:** 10/03/26.

### Integrantes:
- Estrada Zacarias Aldo Axel
- Sánchez Salazar Jazmín

## Instrucciones de compilación/ejecución.

Este programa fue desarrollado en C para sistemas Unix/Linux, ya que utiliza llamadas al sistema y encabezados POSIX como `fork()`, `execvp()`, `waitpid()`, `sigaction()` y `sys/wait.h`.

#### Para compilar y ejecutar el programa se necesita de lo siguiente:

- Sistema operativo Unix/Linux o entorno compatible (WSL).
- Compilador GCC con soporte para el estándar C11.

### Compilación.
Para compilar el programa se utiliza gcc como compilador con el estándar C11
```bash
gcc -Wall -Wextra -std=c11 minishell.c -o minishell
```
### Ejecución.
Ya que se ha compilado el programa se ejecuta con:
```bash
./minishell
```
## Breve Explicación del diseño.

El minishell implementa un ciclo interactivo en el que se muestra un prompt (`minishell$`), se lee una línea de entrada del usuario y se ejecuta el comando solicitado. La lectura de la entrada se realiza con `fgets()` y posteriormente la línea se divide en el comando y sus argumentos utilizando `strtok()`.

Para ejecutar cada comando se utiliza la llamada al sistema `fork()`, que crea un proceso hijo. Este proceso hijo restaura el comportamiento por defecto de la señal `SIGINT` y ejecuta el comando solicitado mediante `execvp()`, lo que permite ejecutar programas del sistema utilizando el `PATH`.

El proceso padre se encarga de esperar la terminación del proceso hijo y continuar con el ciclo del shell. Para ello se utiliza el manejo de señales del sistema, en particular `SIGCHLD`, que permite detectar cuando un proceso finaliza y evitar la creación de procesos zombie.

Finalmente, el minishell ignora la señal `SIGINT` en el proceso padre para evitar que el shell termine cuando el usuario presiona `Ctrl+C`, mientras que los procesos hijos sí pueden ser interrumpidos normalmente.
## Ejemplo de Ejecución.
A continuación se muestra un ejemplo de uso del minishell ejecutando algunos comandos básicos del sistema.

```bash
./minishell

minishell$ echo "Hola mundo"
"Hola mundo"
minishell$ sleep 10
^Cminishell$ pwd
/sistop-2026-2/tareas/1/EstradaAldo-SanchezJazmin
minishell$ ls -l
total 28
-rwxr-xr-x 1 root root 16968 Mar 10 20:33 minishell
-rw-r--r-- 1 root root  4407 Mar 10 20:47 minishell.c
minishell$ exit
```

## Dificultades encontradas y cómo se resolvieron.

El mayor reto que se presentó durante el desarrollo del minishell fue el manejo correcto de los procesos hijos, ya que no bastaba únicamente con crear el proceso hijo y ejecutar el comando, sino que era necesario coordinar adecuadamente tanto el proceso padre como el manejador de la señal `SIGCHLD` sin que existieran errores de sincronización.

Principalmente el problema fue evitar una condición de carrera donde el proceso hijo terminara su ejecución antes de que el proceso padre registrara de forma correcta su PID como proceso en primer plano. Para resolver esto se bloqueó temporalmente la señal `SIGCHLD` antes del `fork()`. Posteriormente el proceso padre registró el PID del hijo y utilizó la función `sigsuspend()` para esperar de manera segura la señal que indica la finalización del proceso hijo.

Otra dificultad importante fue evitar la creación de procesos zombie. Para ello se implementó un manejador de la señal `SIGCHLD`, el cual utiliza `waitpid()` con la opción `WNOHANG` para recolectar los procesos hijos terminados sin bloquear la ejecución del minishell.

También se tuvo que manejar correctamente la señal `SIGINT`. El minishell no debe finalizar cuando el usuario presiona `Ctrl+C`, pero los comandos que se estén ejecutando sí deben poder interrumpirse. Esto se resolvió haciendo que el proceso padre ignore `SIGINT`, mientras que el proceso hijo restaura el comportamiento por defecto antes de ejecutar el comando.

Finalmente, se encontró la dificultad de compilación en Windows, ya que el programa utiliza encabezados y llamadas al sistema propias de Unix/Linux, como `sys/wait.h`, `fork()` y `sigaction()`. Por esta razón, la compilación y ejecución deben realizarse en un entorno Linux o compatible, como WSL.
