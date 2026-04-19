# Tarea 3: Comparación de Planificadores

Alumno: Sergio Quiroz Salazar


## Problema resuelto

En esta tarea implementé distintos algoritmos clásicos de planificación de CPU con el objetivo de comparar su comportamiento ante múltiples cargas de trabajo generadas aleatoriamente.

El programa genera cinco rondas independientes de ejecución, en cada una de las cuales se crean procesos con tiempos de llegada y duración distintos. Posteriormente, cada conjunto de procesos es ejecutado utilizando varios algoritmos de planificación para analizar sus diferencias en desempeño.

Esto permite observar cómo influyen las políticas de planificación sobre el tiempo de espera de los procesos, el tiempo total de retorno y la penalización promedio.


## Entorno de desarrollo

- Lenguaje: Python 3
- Entorno: Linux
- Requisitos: Python 3 instalado

Para ejecutar el programa:

1. Abrir la terminal en este directorio
2. Ejecutar:

## Algoritmos implementados

Los algoritmos de planificación implementados en este programa son:

- FCFS (First Come First Served)
- RR1 (Round Robin con quantum = 1)
- RR4 (Round Robin con quantum = 4)
- SPN (Shortest Process Next)
- FB (Feedback Scheduling con colas multinivel)

Cada algoritmo ejecuta exactamente el mismo conjunto de procesos en cada ronda para garantizar una comparación directa entre resultados.

## Estrategia de simulación de ejecución

Para simular el comportamiento de los algoritmos de planificación se modeló la ejecución del CPU como una línea de tiempo discreta en la que cada unidad representa un instante de ejecución.

Cada proceso es representado mediante:

- identificador
- tiempo de llegada
- duración de ejecución

Durante la simulación, el programa mantiene estructuras de datos dinámicas (listas y colas) que permiten administrar los procesos disponibles en cada instante de tiempo.

Para cada algoritmo:

- FCFS ejecuta los procesos en orden de llegada sin interrupciones
- SPN selecciona el proceso disponible con menor duración
- Round Robin utiliza una cola FIFO y asigna turnos de ejecución según el quantum definido
- FB utiliza múltiples colas de prioridad con quantums crecientes, permitiendo ajustar dinámicamente la prioridad de los procesos según su comportamiento

Este enfoque permite reproducir el comportamiento típico de cada algoritmo y comparar sus métricas de desempeño bajo las mismas condiciones de carga.

## Observaciones

A partir de las ejecuciones realizadas se observó que el algoritmo SPN generalmente produce menores tiempos promedio de espera y menor penalización debido a que prioriza procesos cortos.

El algoritmo FCFS es sencillo de implementar pero puede provocar mayores tiempos de espera cuando procesos largos llegan primero.

Round Robin permite distribuir el uso del CPU de forma más equitativa entre los procesos, aunque puede incrementar el tiempo de espera promedio si el quantum es pequeño.

El algoritmo FB combina múltiples niveles de prioridad y permite adaptar dinámicamente la ejecución de los procesos, favoreciendo aquellos que requieren menos tiempo de CPU en etapas iniciales.


## Conclusión

La comparación entre algoritmos de planificación permite observar cómo diferentes estrategias afectan directamente el desempeño del sistema. Mientras algunos algoritmos priorizan la equidad en la asignación del CPU, otros optimizan el tiempo promedio de espera o la penalización.
