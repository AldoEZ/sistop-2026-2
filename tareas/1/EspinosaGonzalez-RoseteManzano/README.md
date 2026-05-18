
# Tarea 1 – Minishell

Implementación sencilla de un intérprete de comandos tipo shell para la materia de Sistemas Operativos.

## Autoras

Sara Sofia Espinosa Gonzales  
Karina Lizeth Rosete Manzano

## Descripción

El programa implementa un shell básico que permite ejecutar comandos del sistema.
El objetivo principal es entender cómo funcionan los procesos en sistemas Unix usando `fork()` y `exec()`.

Cuando el usuario escribe un comando, el shell:

1. Lee la línea ingresada
2. Separa el comando y sus argumentos
3. Crea un proceso hijo con `fork()`
4. El proceso hijo ejecuta el programa solicitado con `execvp()`
5. El proceso padre espera a que termine o lo deja correr en segundo plano

## Cómo ejecutarlo

En Linux o WSL:

python3 minishell.py

Después aparecerá el prompt:

minishell>

Ahí se pueden escribir comandos del sistema.

## Ejemplos de uso

minishell> ls  
minishell> ls -l  
minishell> echo Hola mundo  
minishell> sleep 5  
minishell> sleep 10 &  
minishell> ps  
minishell> exit  

El símbolo `&` permite ejecutar el proceso en segundo plano.

## Manejo de señales

El programa utiliza dos señales principales.

SIGCHLD  
Se usa para detectar cuando un proceso hijo termina y poder recolectarlo usando `waitpid()`.

SIGINT (Ctrl + C)  
El shell ignora esta señal para no cerrarse accidentalmente, pero los procesos hijos sí mantienen el comportamiento normal.

## Observaciones del programa

- Solo ejecuta comandos simples del sistema.
- No se implementaron pipes (`|`) ni redirecciones (`>` `<`) porque no eran necesarias para la práctica.
- Si el comando no existe, se muestra un mensaje indicando que no fue encontrado.
- Es posible ejecutar procesos en segundo plano usando `&`.

## Comportamiento al usarlo

- Cuando un proceso termina en segundo plano, el shell muestra el PID del proceso.
- Si se presiona `Ctrl + C` mientras el shell está esperando entrada, simplemente vuelve a mostrar el prompt.
- El comando `exit` termina el shell de forma limpia.

## Dificultades encontradas

Durante la implementación fue necesario revisar bien cómo funciona `waitpid()` con la opción `WNOHANG`, ya que si no se usa correctamente el shell puede quedarse bloqueado esperando procesos.

También fue importante manejar correctamente las señales para evitar que queden procesos zombie cuando se ejecutan comandos en segundo plano.

## Comentario final

Aunque es una versión muy simplificada de un shell real como `bash`, permite entender mejor cómo funcionan los procesos y el manejo de señales en sistemas Unix.
