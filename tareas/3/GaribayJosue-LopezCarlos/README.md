# Tarea 3. Comparación de planificadores 
Universidad Nacional Autónoma de México 
Facultad de Ingeniería  
Sistemas Operativos 
Alumnos: 
- Garibay Zamorano Josué Benjamín 
- López López Carlos Daniel 
Fecha de entrega: 16/04/26 

## Planificación de procesos 
En clases vimos lo que es la planificación de procesos que en pocas palabras es la forma que tiene el sistema operativo para poder ejecutar diferentes procesos y el como hacerlo, vimos que existían tres tipos de planificación los de largo plazo, mediano plazo y a corto plazo, enfocándonos especialmente en este último, en la planificación de procesos a corto plazo. 
Esta planificación de procesos a corto plazo también es conocida como despachador y nos ayuda a decidir como compartir la CPU entre los distintos procesos momento a momento. 
Para la planificación de procesos existen diferentes algoritmos los cuales utilizamos para la resolución de esta tarea, como lo son: 
### 1.- FCFS 
Primero llegado, primero servido o también conocido como FIFO primero en llegar, primero en salir, es el más simple de todos pues su proceso de ejecución se basa en que cada proceso es ejecutado cuando el que llego antes que el sea terminado, no tiene preferencias ni prioridad, se basa en orden de llegada. 
Por tal motivo puede perjudicar a aquellos procesos los cuales sean cortos, pues estos pueden esperar mucho tiempo antes de ser ejecutados. 
### 2.- Round Robin (RR) 
Oh por su traducción "Ronda", lo que busca este algoritmo es ser lo más equilibrado posible, es decir beneficiar tanto a los procesos cortos como a los procesos largos, dándoles a cada proceso un tiempo determinado de ejecución determinado por un quantum, donde si el proceso no termina su ejecución durante su tiempo determinado, este regresa al final de la cola junto con los procesos que se vayan insertando. 
Si se agrega un quantum lo suficientemente grande, entonces pasa a tomar la forma de FCFS, por lo que lo mejor es mantener un equilibrio para no tener demasiados cambios al poner un quantum muy pequeño. 
### 3.- Shortest Process Next (SPN) 
Oh también llamado en español como "Proceso más corto a continuación" es un algoritmo el cual calcula cual es el proceso que requiere menos tiempo para su ejecución y el que resulte con menor tiempo en la cola va a ser el siguiente en ser ejecutado. 
Su mayor ventaja es que beneficia a procesos cortos, pero para procesos largos se tiene el riesgo de poder llegar a tener inanición pues nunca van a ser el proceso más corto. 
Para este tipo de casos existen refinamientos como "El proceso más castigado a continuación" el cual busca evitar la inanición de procesos largos al hacer que si un proceso largo es penalizado múltiples veces entonces sea el siguiente a ser ejecutado. 
### 4.- Retroalimentación multinivel (FB) 
Ah comparación de los algoritmos anteriores este es de múltiples colas, donde van a existir dos colas una de mayor prioridad que la otra, donde si en la cola de mayor prioridad un proceso no termina su ejecución en un tiempo determinado este es degradado a una cola de menor prioridad. 
Este algoritmo favorece a procesos  cortos pues un proceso corto puede terminar su ejecución sin ser degradado. 
### 5.- Ronda egoísta (SRR) 
Finalmente tenemos a la ronda egoísta donde de igual forma este es un algoritmo de múltiples colas, donde van a existir dos colas, una de procesos nuevos y otra de procesos aceptados, donde solo se ejecutan los procesos aceptado. 
Tanto la prioridad de los procesos nuevos como la de los procesos aceptados van cambiando, donde cuando la prioridad de un proceso nuevo alcance a la de uno aceptado, este va a entrar a la cola de procesos aceptados para su ejecución. 

## Lenguaje y requerimientos de ejecución  

Para poder ejecutar este programa es necesario tener instalado python, así mismo se debe posicionar en la ruta donde se encuentre el programa y ejecutar la siguiente instrucción: 
$ python Tarea3_GL.py 

## Verificación de la Ronda 1 

Verificando únicamente FCFS de la primera ronda: 
![img](img/T3img1.jpeg)

| Proceso  | Inicio | Fin | T   | E   | P    |
| -------- | ------ | --- | --- | --- | ---- |
| A        | 0      | 2   | 2   | 0   | 1    |
| B        | 3      | 10  | 7   | 0   | 1    |
| C        | 10     | 13  | 10  | 7   | 3.33 |
| D        | 13     | 16  | 12  | 9   | 4    |
| E        | 16     | 18  | 12  | 10  | 6    |
| Promedio |        |     | 8.6 | 5.2 | 3.07 |
Por lo tanto podemos ver que si se cumple nuestro programa para FCFS, por cuestiones de tiempo no abordaremos más casos ni más algoritmos lamentamos el inconveniente :( 

## Dudas y comentarios 

Sobre el desarrollo de está tarea no tuvimos dudas al respecto al momento de estarla realizando. 