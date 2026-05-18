Este proyecto implementa un intérprete de comandos básico (shell) en Python para sistemas Unix/Linux.
El programa permite al usuario ejecutar comandos del sistema utilizando llamadas al sistema como fork() y execvp(), además de manejar correctamente la terminación de procesos hijos mediante la señal SIGCHLD.

La minishell funciona de manera interactiva mostrando un prompt donde el usuario puede escribir comandos del sistema como ls, pwd, echo, sleep, entre otros.

El objetivo del proyecto es comprender el manejo de procesos y señales en sistemas operativos tipo Unix.

Instrucciones de ejecución

Primero se debe abrir una terminal en el directorio donde se encuentra el archivo minishell.py.

Para ejecutar el programa se usa el siguiente comando:

python3 minishell.py

Al ejecutarlo aparecerá el prompt:

minishell>

A partir de ese momento se pueden ejecutar comandos del sistema.

Funcionamiento del programa

El programa sigue el funcionamiento básico de un shell de Unix:

El shell muestra un prompt solicitando un comando.

El usuario escribe un comando.

El programa separa el comando y sus argumentos utilizando shlex.split().

Se crea un proceso hijo utilizando os.fork().

El proceso hijo ejecuta el comando utilizando os.execvp().

El proceso padre maneja la finalización del proceso hijo mediante la señal SIGCHLD.

El comando interno exit permite terminar la ejecución del shell.


Manejo de señales
SIGCHLD

El programa instala un manejador para la señal SIGCHLD, la cual se envía al proceso padre cuando un proceso hijo termina.

El manejador utiliza:

os.waitpid(-1, os.WNOHANG)

para recolectar los procesos hijos terminados sin bloquear la ejecución del shell.
Esto evita la creación de procesos zombie.


SIGINT

El shell ignora la señal SIGINT (Ctrl + C) para evitar que el programa termine accidentalmente.

Sin embargo, los procesos hijos restauran el comportamiento normal de SIGINT, por lo que sí pueden ser interrumpidos por el usuario.


Ejemplo de ejecución
minishell> ls
archivo1.txt
archivo2.txt

minishell> pwd
/home/usuario

minishell> echo "Hola mundo"
Hola mundo

minishell> sleep 3

[Proceso 1234 terminó con código 0]

minishell> exit
Saliendo de minishell...


Dificultades encontradas y solución
Manejo de procesos zombie

Uno de los problemas al trabajar con procesos hijos es la generación de procesos zombie si estos no son recolectados correctamente.

Para evitar este problema se utilizó un manejador de la señal SIGCHLD que llama a waitpid() con la opción WNOHANG.



