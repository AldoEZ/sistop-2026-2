# Minishell en Python

**Autores**
* Santiago Bello
* Baruc López

En esta tarea se implementa un interprete de comandos basicos en Python, el programa es compatible con sistemas Unix/Linux.

## Instrucciones de compilacion y ejecución

Ya que esta escrito en Pyhton, no se necesita de compilacion previa.
Se debe verificar que este instalado Pyhton3 en el sistema y ejecutar el programa mediante:

```bash
python3 T01.py
```

## Explicación del diseño

En este programa:
1. Se utiliza os.fork() para crear un proceso hijo
2. En el proceso hijo, se utiliza os.exexvp() para ejecutar el comando usado pr el usuario
3. Para evitar que el shell principal se bloquee esperando comandos largos, se tiene un manejador asincrono para la señal SIGCHLD. En este manejador se usa os.waitpid(-1,os.WNOHANG) para limpiar los porcesos "zombies" en segundo plano
4. El proceso padre ignora la señal SIGINT de Ctrl+C para que asi el minishell se pueda seguir ejecutando y no se cierre por accidente si el usuario intenta cancelar un comando en ejecucion

## Ejemplo de ejecución
```bash
minishell> ls -l
minishell> total 4
-rwxrwxrwx 1 root root 3649 Mar  8 16:52 T01.py
minishell> sleep 5
minishell> exit
Terminando minishell...
```

## Dificultades encontradas

Debido a que los comandos os.fork() son del kernel de linux, el codigo no se podia ejecutar en Windows sin que saltase un error, para resolverlo, se tuvo que instalar Windows Subsystem for Linux con Ubuntu para tener asi un entorno de ejecucion que si permitiera correr el programa.
Otra dificultad fue que al inicio no quedaba muy claro como hacer que el prompt se regrsara de inmediato al hacer comandos como el sleep, esto se pudo resolver con el uso de WNOHANG dentro del manejador de la señal SIGCHLD.

