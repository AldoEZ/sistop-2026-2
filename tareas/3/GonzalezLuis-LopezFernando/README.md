# Simulador de Algoritmos de Planificación de Procesos

## Planteamiento del problema
Este proyecto es una implementación en Python que simula y compara distintos algoritmos de planificación de procesos de sistemas operativos frente a cargas de trabajo generadas aleatoriamente. El objetivo es analizar el rendimiento de algoritmos sencillos (FCFS, RR, SPN) y con un enfoque avanzado utilizando colas múltiples (FB).

El programa evalúa métricas fundamentales como el Tiempo de retorno (T), Tiempo de espera (E) y la Proporción de penalización (P), acompañando los resultados numéricos con un esquema visual del orden exacto en que la CPU atendió a cada proceso.

## Lenguaje y entorno de desarrollo
- **Lenguaje:** Python 3
- **Bibliotecas usadas:** `random` (para la generación de cargas simuladas).

### Entorno y Requisitos
El programa no requiere de la instalación de bibliotecas externas complejas por lo que corre nativamente con una instalación estándar de Python.
- **Para Windows (Entorno principal de pruebas):**
  Basta con abrir la consola (PowerShell o CMD), navegar a la carpeta donde se encuentra guardado el archivo y ejecutar:
  ```powershell
  python planificacion.py
  ```

- **Para distribuciones Linux:** Abre la terminal en el directorio del código fuente y ejecuta:
```bash
python3 planificacion.py
```


## Estrategia de comparación

Para la comparación, se ha generado un bloque de 5 procesos por ronda que comparten el mismo tiempo de llegada y tiempos de ráfaga aleatorios para que todos los algoritmos sean evaluados bajo exactamente el mismo estrés y condiciones.

A continuación se detalla brevemente la lógica implementada para cada uno:

- **FCFS (First Come, First Serve):** La lógica implementada atiende los procesos en el orden estricto de llegada. No es apropiativo, por lo que una vez que un proceso toma la CPU, se ejecuta ininterrumpidamente hasta terminar su ráfaga.

- **RR (Round Robin - Quantum 1 y 4):** Se simuló mediante el uso de una lista que actúa como cola. Los procesos se forman y toman la CPU durante un máximo establecido por el "quantum". _Nota importante en la implementación:_ Es crucial revisar qué procesos nuevos van llegando al sistema justo en el momento en que se procesa el quantum actual, para agregarlos a la cola antes de mandar al final al proceso actual que acaba de ser interrumpido.

- **SPN (Shortest Process Next):** La lógica busca, de entre los procesos que ya llegaron al sistema en el `tiempo_actual`, cuál tiene la ráfaga de CPU total más pequeña (`t`). Al no ser apropiativo, el proceso que gana se ejecuta hasta el final.

- **FB (Multilevel Feedback):** Se utilizaron 3 listas distintas para emular tres colas de prioridad (Alta, Media y Baja). Todos los procesos entran inicialmente a la cola de alta prioridad. Para simplificar el manejo de penalización, el quantum global es de 1. Si un proceso consume su tiempo de CPU y no ha terminado, es castigado moviéndose a la cola inferior.

## Guía de Ejecución

Para alterar la cantidad de simulaciones ejecutadas basta simplemente con ejecutar el archivo e incluir un número que representa la cantidad de simulaciones ejecutadas.

Por defecto, está establecido en 5 (constante `NUM_RONDAS`), lo que mostrará en la terminal 5 bloques completos con sus respectivas cargas generadas de forma aleatoria, los cálculos de (T, E, P) y la línea de tiempo simulada carácter por carácter para cada uno de los 5 algoritmos solicitados.
