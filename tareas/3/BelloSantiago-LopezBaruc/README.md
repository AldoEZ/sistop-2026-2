# DOCUMENTACIÓN - TAREA 03: COMPARACIÓN DE PLANIFICADORES

**Autores:** * Bello Sanchez Santiago Arath
* López Romero David Baruc

---

## EJECUCIÓN DEL PROGRAMA
El simulador fue desarrollado en Python 3. No requiere la instalación de ninguna biblioteca externa, ya que utiliza únicamente las bibliotecas nativas `random` (para la generación de ráfagas aleatorias) y `string` (para la asignación de IDs de procesos). 

Para ejecutarlo, basta con abrir la terminal en el directorio donde se encuentra el archivo y ejecutar el comando:

    python3 compara_planif.py

**Ejemplo de la salida de la simulación:**
```text
- Ronda 1:
  A: 0, t=3; B: 3, t=7; C: 5, t=5; D: 5, t=7; E: 5, t=4 (tot:26)
  FCFS : T=11.60, E=6.40, P=2.34
      AAABBBBBBBCCCCCDDDDDDDEEEE
  RR1  : T=15.40, E=10.20, P=2.86
      AAABBBCDEBCDEBCDEBCDEBCDDD
  RR4  : T=15.00, E=9.80, P=2.76
      AAABBBBCCCCDDDDEEEEBBBCDDD
  SPN  : T=10.80, E=5.60, P=2.01
      AAABBBBBBBEEEECCCCCDDDDDDD
  FB   : T=15.20, E=10.00, P=2.77
      AAABBCDECDEBCDEBCDEBCDBDBD

- Ronda 2:
  A: 0, t=2; B: 0, t=3; C: 1, t=6; D: 1, t=7; E: 3, t=3 (tot:21)
  FCFS : T=10.40, E=6.20, P=2.55
      AABBBCCCCCCDDDDDDDEEE
  RR1  : T=12.40, E=8.20, P=2.87
      ABACDBECDBECDECDCDCDD
  RR4  : T=11.40, E=7.20, P=2.54
      AABBBCCCCDDDDEEECCDDD
  SPN  : T=9.00, E=4.80, P=1.87
      AABBBEEECCCCCCDDDDDDD
  FB   : T=13.20, E=9.00, P=3.24
      ABCDEABCDEBCDECDCDCDD

- Ronda 3:
  A: 0, t=5; B: 1, t=4; C: 4, t=4; D: 4, t=3; E: 6, t=5 (tot:21)
  FCFS : T=9.80, E=5.60, P=2.45
      AAAAABBBBCCCCDDDEEEEE
  RR1  : T=13.20, E=9.00, P=3.27
      AABABACDBAECDBECDECEE
  RR4  : T=10.40, E=6.20, P=2.56
      AAAABBBBACCCCDDDEEEEE
  SPN  : T=9.40, E=5.20, P=2.22
      AAAAADDDBBBBCCCCEEEEE
  FB   : T=15.00, E=10.80, P=3.57
      ABABCDECDEABCDEABCEAE

- Ronda 4:
  A: 0, t=6; B: 3, t=4; C: 5, t=7; D: 6, t=2; E: 8, t=2 (tot:21)
  FCFS : T=10.20, E=6.00, P=3.49
      AAAAAABBBBCCCCCCCDDEE
  RR1  : T=10.80, E=6.60, P=3.06
      AAAABABCADBCEDBCECCCC
  RR4  : T=10.20, E=6.00, P=3.04
      AAAABBBBAACCCCDDEECCC
  SPN  : T=7.40, E=3.20, P=1.61
      AAAAAADDEEBBBBCCCCCCC
  FB   : T=10.80, E=6.60, P=2.39
      AAABBCDCEDEBCABCACACC

- Ronda 5:
  A: 0, t=2; B: 3, t=2; C: 6, t=4; D: 8, t=6; E: 10, t=7 (tot:21)
  FCFS : T=5.80, E=1.60, P=1.24
      AA-BB-CCCCDDDDDDEEEEEEE
  RR1  : T=6.80, E=2.60, P=1.42
      AA-BB-CCCDCDEDEDEDEDEEE
  RR4  : T=6.60, E=2.40, P=1.37
      AA-BB-CCCCDDDDEEEEDDEEE
  SPN  : T=5.80, E=1.60, P=1.24
      AA-BB-CCCCDDDDDDEEEEEEE
  FB   : T=8.00, E=3.80, P=1.70
      AA-BB-CCDDEECDECDEDEDEE
```

## ESTRATEGIAS DE SIMULACIÓN Y ESTRUCTURAS DE DATOS
Para abordar la simulación, se descartó el cálculo matemático por "saltos de ráfaga" y se optó por un modelo basado en eventos de tiempo (Tick-based).

* **Reloj del Sistema:** Se implementó un ciclo `while` que representa el reloj del CPU avanzando milisegundo a milisegundo (`t += 1`). Esto permitió registrar de manera exacta los tiempos muertos (representados con `-` en el diagrama de Gantt) cuando el CPU se encuentra ocioso esperando llegadas futuras.
* **Colas de Listos:** Se utilizó una lista dinámica (`ready`) para gestionar los procesos. Dependiendo del algoritmo en ejecución, la lista altera su comportamiento:
  * Para **FCFS**: Se ordena dinámicamente basándose en el tiempo de llegada.
  * Para **SPN**: Se ordena dinámicamente basándose en el tiempo total de duración del proceso.
  * Para **Round Robin (RR1 y RR4)**: Funciona como una estructura FIFO estricta.

## REFINAMIENTOS Y DECISIONES DE IMPLEMENTACIÓN
Se tomaron dos decisiones críticas de diseño para cumplir con las condiciones del planteamiento:

1. **Resolución de Ambigüedad en Round Robin:** Ante la duda planteada sobre si el orden correcto al expirar un quantum y recibir un nuevo proceso es `ABABC...` o `ABACB...`, el planificador fue diseñado para dar prioridad a las **nuevas llegadas**. En el mismo milisegundo, los procesos recién llegados se forman primero en la cola, y el proceso que acaba de ser interrumpido por el CPU se forma detrás de ellos.
2. **Algoritmo de Colas Múltiples (Feedback):** Para extender la comparativa y alcanzar la puntuación máxima, se implementó el algoritmo de Retroalimentación Multinivel (FB). Se utilizó un diccionario (`fb_queues`) con 20 niveles de prioridad. Todos los procesos ingresan en el nivel de máxima prioridad (Nivel 0) y son penalizados descendiendo de nivel cada vez que agotan un tick de CPU, garantizando que los procesos cortos abandonen rápido el sistema.

## ÁREA DE MEJORA
Actualmente el diagrama de Gantt generado en consola es muy visual y útil para verificar ráfagas pequeñas. Sin embargo, si quisiéramos someter al simulador a un estrés real (por ejemplo, cargas de 1000 procesos con duraciones largas), la cadena de texto en consola sería ilegible. Una mejora interesante sería exportar los resultados de las variables métricas (T, E y P) al finalizar las rondas, para poder graficar las tendencias de penalización de cada algoritmo en herramientas externas.