Tarea 1 - MéridaFrancisco - QuezadaLeonardo


#  INSTRUCCIONES DE COMPILACIÓN / EJECUCIÓN


Trabajamos con un código en lenguaje Python llamado “MéridaFrancisco-QuezadaYépez.py”:

Para ejecutar el programa hacer: 
- python3 T01.py
- o ./T01.py

Una vez dentro aparecerá el prompt “miniShell🏀>:”, ahí se pueden escribir los comandos del sistema.

Como requisitos del programa se necesitará tener instalado Python 3 y ejecutarlo en un sistema tipo Unix.


 
# EXPLICACIÓN DE DISEÑO
 

Para el diseño del shell, se sigue la siguiente secuencia:

  1. Se realiza el manejo de señales
  2. Muestra el prompt “miniShell🏀>:”.
  3. Permite el ingreso de comandos.  
  4. Parsea el comando y argumentos ingresados con la función “shlex.split()”.
  5. Si se usa el comando “exit”, finaliza el bucle y el programa.
  6. Crea un proceso hijo y manda a ejecutar el comando ingresado.
  7. Repite el proceso.



###  MANEJO DE SEÑALES

En el shell hacemos manejo de la señal “SIGCHLD” y la señal “SIGINT”:

SIGCHLD

Lo manejamos con la función “sigchld_handler” para evitar procesos zombies. Para esto recolectamos  los procesos hijos finalizados empleando “os.waitpid(-1,os.WNOHANG)” de forma que la llamada no bloquea al proceso padre.

SIGINT

El proceso padre debe ignorar Ctrl + C, por lo que configuramos el manejo de SIGINT usando  signal.signal estableciendo SIG_IGN para ignorar dicha señal.

Posteriormente, se restaura el funcionamiento por defecto de la señal para los procesos hijos usando SIG_DFL.


###  CREACIÓN DE PROCESOS

Para la creación de procesos hijos se usa “os.fork()”

El proceso hijo restablece la señal SIGINT y ejecuta el comando solicitado mediante la función “os.execvp()”

El proceso padre no espera la finalización del proceso hijo, de forma que se puede seguir empleando el shell. 


#  EJEMPLO DE EJECUCIÓN

- usuario:~$ python3 T01.py
- miniShell🏀>: ls
- miniShell🏀>: <Programas dentro del directorio de ejecución>
- miniShell🏀>: echo “Hola desde el miniShell”
- miniShell🏀>: Hola desde el miniShell
- miniShell🏀>: exit
- usuario:~$


##  DIFICULTADES ENCONTRADAS Y SOLUCIONES

1) Una de las dificultades que tuvimos fue el manejo de la señal SIGINT para lograr que Ctrl +C sólo afecte a los procesos hijos: 

Para lograrlo, al inicio del proceso padre ignoramos las señales SIGINT usando signal.signal con SIG_IGN. Posteriormente los procesos hijos restauran el comportamiento normal de  SIGINT utilizando SIG_DFL. 

2) Otra dificultad se presentó durante la impresión del prompt y las salidas de los procesos hijos, ya que estas podían encimarse debido a que el proceso padre no espera a que los procesos hijos terminen: 

Para lograr una impresión más limpia, decidimos introducir una pausa de 0.01 segundos en el proceso padre (usando time.sleep(0.01)) antes de imprimir el prompt, evitando así que las salidas se encimen.

