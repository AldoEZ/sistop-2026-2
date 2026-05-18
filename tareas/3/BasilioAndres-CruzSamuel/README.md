# Simulador de Planificación de Procesos (CPU)

Este script es un simulador basado en *ticks* (unidades discretas de tiempo) que evalúa el rendimiento de distintos algoritmos de planificación de sistemas operativos bajo cargas de trabajo aleatorias.

## Algoritmos Implementados
1. **FCFS (First-Come, First-Served):** Los procesos se ejecutan en el orden exacto en el que llegan a la cola de listos. No es expropiativo.
2. **RR (Round Robin):** Algoritmo expropiativo. Asigna un tiempo máximo de uso continuo de CPU (*quantum*) a cada proceso. Si el proceso no termina en ese tiempo, se interrumpe y se manda al final de la cola. Evaluado con $q=1$ y $q=4$.
3. **SPN (Shortest Process Next):** El planificador selecciona el proceso en espera que tenga la ráfaga total de ejecución más corta. No es expropiativo.
4. **FB (Feedback / Retroalimentación):** Implementa 3 colas multinivel. Todos los procesos entran por el nivel de mayor prioridad. Si agotan su quantum en ese nivel, son penalizados bajando de prioridad. Favorece a los procesos interactivos y penaliza a los limitados por CPU.

## Métricas Calculadas
Por cada proceso y como promedio global de la ronda, el simulador reporta:
* **T (Tiempo de Estancia):** Tiempo desde que el proceso llega hasta que termina por completo.
* **E (Tiempo de Espera):** Tiempo que el proceso pasó inactivo en la cola de listos.
* **P (Índice de Penalización):** Relación entre el Tiempo de Estancia y la Ráfaga Total de CPU ($P = T / t$).

## Flujo del Programa
1. Se generan 5 rondas independientes.
2. En cada ronda, se instancian 5 procesos con tiempos de llegada (0-12) y ráfagas de CPU (2-7) aleatorios.
3. Se evalúa la misma carga de procesos en todos los algoritmos para garantizar una comparación justa.
4. Se imprime el diagrama visual de la línea de tiempo y la tabla de métricas.
