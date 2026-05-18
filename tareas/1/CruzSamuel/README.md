# Tarea 1: Implementación de un intérprete de comandos (Minishell)

**Materia:** Sistemas Operativos  
**Alumno:** Samuel Santiago Cruz Macedo  
**Fecha:** 10 de marzo de 2026

---

## Introducción al proyecto
Este proyecto consiste en el desarrollo de una minishell programada en Python. El objetivo primordial fue entender a fondo cómo interactúa un programa de usuario con el sistema operativo de Linux para gestionar recursos básicos. A través de este código, se exploran conceptos fundamentales como la creación de procesos, la ejecución de archivos binarios y la administración de señales de interrupción, que son la base de cualquier sistema operativo moderno.



## Funcionamiento y diseño del programa
La lógica del programa se basa en un ciclo infinito que se mantiene a la escucha de las órdenes del usuario. El primer paso es la captura de la entrada mediante el prompt `terminal>`. Esta cadena de texto se procesa utilizando el método `.split()`, lo cual es vital para separar el nombre del comando de sus parámetros. Por ejemplo, si el usuario escribe `ls -l -a`, el programa identifica que el binario a ejecutar es `ls` y que debe pasarle una lista con los argumentos adicionales.

La ejecución real del comando ocurre gracias a la llamada al sistema `os.fork()`. Esta función genera un proceso hijo que es una copia del shell original. Dentro de este proceso hijo, se invoca `os.execvp()`, una función encargada de buscar el programa solicitado en las rutas del sistema (PATH) y reemplazar el código del proceso hijo con el del nuevo programa.A la vez que pasa todo eso, el proceso padre (la terminal) se mantiene en un estado de espera controlada para asegurar que el usuario no pueda ingresar nuevos comandos hasta que el anterior haya finalizado, manteniendo así la coherencia en la salida de datos.

### Administración de señales del sistema
Para lograr una terminal estable y funcional fue necesario programar el manejo de señales asíncronas. La señal `SIGCHLD` es fundamental en este diseño. Se configuró un manejador que detecta automáticamente cuándo un proceso hijo ha terminado su ejecución para realizar la limpieza de sus recursos en la tabla de procesos del sistema. Se utilizó la opción `WNOHANG` para que esta recolección ocurra en segundo plano, permitiendo que el shell siga operando sin interrupciones.



Por otro lado, se gestionó la señal `SIGINT` (producida por Ctrl+C). En una terminal estándar, esta señal cerraría el programa inmediatamente. Para evitar que la minishell se cierre accidentalmente, se configuró al proceso padre para ignorar esta interrupción. Sin embargo, para que el usuario aún pueda detener procesos externos que estén tardando demasiado (como un `sleep`), la señal se restaura a su comportamiento original únicamente dentro del proceso hijo justo antes de realizar la ejecución del comando.

## Instrucciones para el usuario
Dado que el programa utiliza llamadas al sistema exclusivas de Unix, es estrictamente necesario contar con un entorno Linux, macOS o el Subsistema de Linux para Windows (WSL). El script se ejecuta desde la terminal mediante el comando `python Minishell.py`.

Una vez iniciada la minishell, se pueden introducir comandos habituales del sistema operativo. Para finalizar la sesión de trabajo de manera limpia, el usuario tiene dos opciones: escribir el comando `exit` o utilizar el atajo de teclado `Ctrl+D`, el cual envía una señal de fin de archivo (EOF) que el programa interpreta para cerrar el ciclo de ejecución.

## Retos y dificultades técnicas
El principal obstáculo durante el desarrollo fue la incompatibilidad entre sistemas operativos. Al trabajar inicialmente sobre un entorno Windows, el módulo `signal` de Python no permitía utilizar `SIGCHLD`, ya que es una señal que no existe en la arquitectura de Windows. Esto requirió la migración del proyecto a un entorno WSL para poder validar que el recolector de procesos y la bifurcación de hilos de ejecución funcionaran acorde a lo solicitado en la tarea.

Otro reto importante fue la sincronización del prompt en la pantalla. En las primeras versiones, el texto `terminal>` se imprimía inmediatamente después de lanzar el proceso hijo, lo que provocaba que la salida del comando se encimara con la nueva línea de entrada, creando un desorden visual. La solución consistió en implementar una espera síncrona en el proceso padre mediante `os.waitpid`, asegurando que el shell recupere el control únicamente cuando el proceso hijo haya entregado sus resultados finales.

## Ejemplos de ejecución
A continuación se detalla una sesión de prueba para demostrar las capacidades del intérprete:

```text
terminal> ls -l
(Se despliega correctamente la lista de archivos del directorio actual)

terminal> echo "Prueba de terminal para Sistemas Operativos"
"Prueba de terminal para Sistemas Operativos"

terminal> sleep 15
^C (Se presiona la interrupción; el comando se detiene pero la shell sigue activa)

terminal> comando_inexistente
Error: No se encontró el comando 'comando_inexistente'

terminal> exit
Saliendo de la minishell...