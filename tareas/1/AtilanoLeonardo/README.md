# Minishell - Tarea 1.

Alumno: Atilano Velázquez Leonardo
Asignatura: Sistemas Operativos
NumCuenta: 321331656


# Instrucciones:

Este script está construido usando llamadas al sistema de POSIX (fork, exec, wait), por lo que es obligatorio ejecutarlo en un entorno Unix/Linux.

Para correr el shell, simplemente se abre la terminal en la carpeta donde está el código y se ejecuta el script "scriptSO.py":

Para salir del minishell de forma limpia, se escribe el comando 'exit'.


# Explicación del diseño:

El proyecto está escrito en Python utilizando las bibliotecas 'os' y 'signal' para poder interactuar a bajo nivel con el sistema operativo. La lógica principal se divide en estas partes:

1. Lectura y parser: El shell corre en un ciclo infinito while true. Para separar el comando de sus argumentos utilizamos la función 'shlex.split()'. Esto es muy útil porque respeta el texto entre comillas (por ejemplo, si queremos hacer un ' echo "Hola mundo" ' lo trata como un solo argumento y no lo rompe).

2. Creación de procesos: Por cada comando ingresado, hacemos un 'os.fork()'.
El proceso hijo utiliza 'os.execvp()' para reemplazar su imagen de memoria y ejecutar el programa que el usuario pidió (buscándolo automáticamente en las variables de entorno PATH).
El proceso padre evalúa si el usuario puso un ampersand (&) al final. Si no lo puso, el padre usa 'os.waitpid()' para quedarse esperando a que el hijo termine. Si sí lo puso, el padre se sigue de largo y te devuelve el prompt inmediatamente.

3. Manejo de señales:
SIGINT (Ctrl + C): Si el usuario presiona Ctrl + C, el comportamiento por defecto de Python es matar el programa. Sobrescribimos esto con un manejador para que solo imprima un salto de línea y vuelva a mostrar el prompt limpio, igual que lo hace Bash.
SIGCHLD: Cuando mandamos un proceso al fondo con '&', el padre no lo espera. Para que esos procesos liberen sus recursos al terminar se implementó un manejador que usa 'waitpid(-1, os.WNOHANG)', el cual limpia al hijo sin congelar nuestro shell principal.


# Dificultades encontradas y cómo se resolvieron:

1. Entorno de sistema operativo compatible: Al inicio intenté correr y probar el script directamente en la terminal de mi IDE PyCharm. Me arrojaba errores porque la arquitectura de Windows no entiende el comando 'os.fork()'. La solución fue configurar e integrar el subsistema de Ubuntu (WSL) dentro del IDE.

2. Conflictos de red y virtualización anidada: Intenté montar el entorno Linux usando una máquina virtual pero me encontré con problemas de configuración de red y restricciones de Windows que no me permitían instalar WSL dentro de la máquina virtual. Para no pelear con adaptadores de red, instalé WSL2 directamente de forma nativa en mi PC principal. Esto me dio un entorno Linux algo más directo.

3. Manejo del Ctrl + C en los hijos: Me di cuenta que al configurar el manejador de 'SIGINT' en el padre, los procesos hijos heredaban esa inmunidad. Si un hijo se quedaba trabado, ya no lo podía matar con Ctrl + C. Para arreglarlo, agregué la línea 'signal.signal(signal.SIGINT, signal.SIG_DFL)' justo después del fork() dentro del bloque del hijo. Esto restaura el comportamiento normal: si hago Ctrl + C, mato al proceso corriendo, pero mi minishell sobrevive.