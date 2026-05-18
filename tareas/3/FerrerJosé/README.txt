Problema resuelto
-----------------
Se desarrolló un programa para comparar distintos algoritmos de
planificación de procesos sobre varias cargas aleatorias.

El objetivo es mostrar que no basta con evaluar un algoritmo sobre una
sola carga, sino que conviene compararlos en varias ejecuciones para
observar tendencias.

Lenguaje y entorno de desarrollo
--------------------------------
El programa fue desarrollado en Python 3.

Para ejecutarlo se necesita:
- Tener Python 3 instalado
- Guardar el archivo con nombre: compara_planif.py
- Ejecutarlo desde terminal con:

  python3 compara_planif.py

En Windows también puede ejecutarse con:

  python compara_planif.py

Algoritmos implementados
------------------------
Se implementaron los siguientes algoritmos de planificación:

- FCFS (First Come, First Served)
- RR1 (Round Robin con quantum = 1)
- RR4 (Round Robin con quantum = 4)
- SPN (Shortest Process Next)

Estrategia de comparación
-------------------------
El programa genera cinco cargas aleatorias de procesos. Cada proceso
tiene:
- un identificador (A, B, C, ...)
- un tiempo de llegada
- una duración

Cada carga se ejecuta con todos los algoritmos implementados y se
calculan las siguientes métricas promedio:

- T: tiempo de retorno promedio
- E: tiempo de espera promedio
- P: penalización promedio

Además, se imprime un esquema visual de ejecución para cada algoritmo,
mostrando en cada unidad de tiempo qué proceso fue ejecutado.

Esquema visual
--------------
El esquema visual representa la secuencia de ejecución de los procesos.
Por ejemplo:

AAABBBBBCCDDDDEEE

Esto indica qué proceso ocupó el CPU en cada instante.