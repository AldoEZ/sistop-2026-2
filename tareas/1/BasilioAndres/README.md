# Tarea 1: Implementación de un intérprete de comandos mínimo (minishell)

**Author:** Andrés Basilio (BassAndres)

## Instrucciones de compilación/ejecución
Para compilar el código fuente desde la terminal de Linux, asegúrate de estar en el directorio donde guardaste el archivo y ejecuta el compilador gcc con el siguiente comando:

    gcc minishell.c -o minishell

Una vez compilado, para iniciar el shell ejecuta:

    ./minishell

## Breve explicación del diseño
El programa está escrito en C y se basa en un ciclo while(1) que mantiene el minishell activo. Su funcionamiento se divide en tres partes clave:

1. Lectura y parseo:
   - Se imprime el prompt "minishell>" y se lee la entrada del usuario.
   - Se usa la función strtok() para separar el comando principal de sus argumentos y guardarlos en un arreglo terminado en NULL.

2. Creación de procesos:
   - Se utiliza la llamada al sistema fork() para crear un proceso hijo.
   - En el hijo se llama a execvp() para ejecutar el comando solicitado.
   - El proceso padre espera con waitpid() a que termine la ejecución en primer plano.

3. Manejo de señales:
   - Se modifica el comportamiento de SIGINT (Ctrl+C) y SIGCHLD para evitar que el shell termine por error o acumule procesos zombie.

## Ejemplo de ejecución
    minishell> ls -l
    total 24
    -rwxrwxr-x 1 andresbasilio041 andresbasilio041 16800 mar  8 18:40 minishell
    -rw-rw-r-- 1 andresbasilio041 andresbasilio041  2300 mar  8 18:40 minishell.c
    -rw-rw-r-- 1 andresbasilio041 andresbasilio041  1500 mar  8 18:40 README.md
    minishell> pwd
    /home/andresbasilio041/sistop-2026-2/tareas/1/BasilioAndres
    minishell> sleep 5
    ^Cminishell> exit

## Dificultades encontradas y cómo se resolvieron
1. El shell se cerraba al usar Ctrl+C (SIGINT)

   Dificultad: Al ejecutar un comando largo (sleep 10) y presionar Ctrl+C, también se mataba el minishell.
   Solución: En el proceso padre se usó signal(SIGINT, SIG_IGN) para ignorar la señal. En el hijo, antes de execvp(), se agregó signal(SIGINT, SIG_DFL) para que los comandos sí pudieran cancelarse con Ctrl+C.

2. Acumulación de procesos zombies (SIGCHLD)

   Dificultad: Los procesos hijos terminados quedaban en la tabla de procesos como zombies.
   Solución: Se configuró un manejador para SIGCHLD con sigaction. En la función del manejador se implementó:
       while (waitpid(-1, NULL, WNOHANG) > 0);
   Usar WNOHANG permitió limpiar procesos hijos de forma asíncrona sin bloquear el prompt principal.
