# Tarea 03: Comparación de planificadores
**Fecha de entrega:** 16/04/26.

### Integrantes:
- Estrada Zacarias Aldo Axel
- Sánchez Salazar Jazmín

## Instrucciones de compilación/ejecución.

Este programa fue desarrollado en C++ para sistemas Unix/Linux, Windows y MacOS. En nuestro caso, fue en un entorno Windows.

#### Para compilar el programa se necesita lo siguiente:
- Sistema operativo Unix/Linux o entorno compatible (WSL en Windows).
- Compilador G++ (GCC para C++) con soporte para C++.

### Compilación.
Para compilar el programa se utiliza g++ como compilador (version 14.1.0).
```bash
g++ planificadores.cpp -o planificadores
```
### Ejecución.
Ya que se ha compilado el programa se ejecuta con:
```bash
./planificadores
```
## Breve Explicación del diseño.
El código del programa está organizado de manera que separa los procesos, los algoritmos de planificación y el cálculo de resultados. Se utiliza una estructura llamada `Proceso` para representar cada tarea con sus datos, y funciones distintas para cada algoritmo (FCFS, Round Robin, SPN y Feedback), lo que permite compararlos fácilmente usando los mismos procesos.Además, el programa genera diversos conjuntos de procesos de forma aleatoria y ejecuta varias rondas de simulación, lo que permite observar el comportamiento de los algoritmos en diferentes escenarios y comparar sus resultados más allá de un solo caso. La simulación avanza paso a paso, ejecutando procesos y registrando el orden en que se atienden, lo cual facilita la verificación manual de los resultados. Al final, se calculan métricas como tiempo de retorno, espera y penalización. Lo anterior, permite agregar o modificar algoritmos sin afectar al resto del programa.

## Ejemplo de Ejecución.
En la ejecución del programa se generan distintos conjuntos de procesos y se comparan los algoritmos de planificación (tomando en cuenta que en cada ejecución del programa se generan los conjuntos de procesos de forma aleatoria, variando los resultados en cada ejecución):

```bash
./planificadores

- Caso de ejemplo de la tarea:
  A: 0, t = 3; B: 1, t = 5; C: 3, t = 2; D: 9, t = 5; E: 12, t = 5

   FCFS: T = 6.2, E = 2.2, P = 1.74
  AAABBBBBCCDDDDDEEEEE
  RR1 : T = 7.6, E = 3.6, P = 1.98
  ABABCABCBDBDEDEDEDEE
  RR4 : T = 7.2, E = 3.2, P = 1.88
  AAABBBBCCBDDDDEEEEDE
  SPN : T = 5.6, E = 1.6, P = 1.32
  AAACCBBBBBDDDDDEEEEE
  FB  : T = 8.8, E = 4.8, P = 2.25
  ABACBBACBDDDEEEBDDEE

- Ronda 1
  A: 0, t = 8; B: 1, t = 7; C: 4, t = 4; D: 5, t = 1; E: 5, t = 4
  FCFS: T = 14.2, E = 9.4, P = 5.30
  AAAAAAAABBBBBBBCCCCDEEEE
  RR1 : T = 16.0, E = 11.2, P = 3.38
  ABABACBDEACBEACBEACBEABA
  RR4 : T = 15.0, E = 10.2, P = 4.66
  AAAABBBBCCCCAAAADEEEEBBB
  SPN : T = 11.2, E = 6.4, P = 2.71
  AAAAAAAADCCCCEEEEBBBBBBB
  FB  : T = 16.2, E = 11.4, P = 3.17
  ABAACDEBBCCEEAAAABBBBCEA

- Ronda 2
  A: 0, t = 1; B: 3, t = 7; C: 5, t = 6; D: 8, t = 6; E: 11, t = 8
  FCFS: T = 10.4, E = 4.8, P = 1.71
  A__BBBBBBBCCCCCCDDDDDDEEEEEEEE
  RR1 : T = 14.6, E = 9.0, P = 2.36
  A__BBCBCBDCBDECBDECBDECDEDEEEE
  RR4 : T = 13.6, E = 8.0, P = 2.22
  A__BBBBCCCCBBBDDDDEEEECCDDEEEE
  SPN : T = 10.4, E = 4.8, P = 1.71
  A__BBBBBBBCCCCCCDDDDDDEEEEEEEE
  FB  : T = 14.0, E = 8.4, P = 2.27
  A__BBCBBDCCEDDEEBBBCCCDDDEEEEE

- Ronda 3
  A: 0, t = 3; B: 2, t = 8; C: 5, t = 2; D: 8, t = 2; E: 10, t = 6
  FCFS: T = 7.6, E = 3.4, P = 2.29
  AAABBBBBBBBCCDDEEEEEE
  RR1 : T = 7.8, E = 3.6, P = 1.83
  AABABCBCBDBEDBEBEBEEE
  RR4 : T = 7.2, E = 3.0, P = 1.94
  AAABBBBCCBBBBDDEEEEEE
  SPN : T = 7.6, E = 3.4, P = 2.29
  AAABBBBBBBBCCDDEEEEEE
  FB  : T = 8.0, E = 3.8, P = 1.93
  AABABCBBDCEDEEBBBBEEE

- Ronda 4
  A: 0, t = 5; B: 2, t = 5; C: 3, t = 1; D: 4, t = 3; E: 4, t = 2
  FCFS: T = 8.6, E = 5.4, P = 3.99
  AAAAABBBBBCDDDEE
  RR1 : T = 9.6, E = 6.4, P = 3.01
  AABACBDEABDEABDB
  RR4 : T = 10.6, E = 7.4, P = 3.89
  AAAABBBBCDDDEEAB
  SPN : T = 6.6, E = 3.4, P = 2.23
  AAAAACEEDDDBBBBB
  FB  : T = 9.2, E = 6.0, P = 2.75
  AABCDEAABBDDEABB

- Ronda 5
   A: 0, t = 4; B: 2, t = 6; C: 2, t = 2; D: 2, t = 2; E: 2, t = 7
  FCFS: T = 10.6, E = 6.4, P = 3.21
  AAAABBBBBBCCDDEEEEEEE
  RR1 : T = 12.6, E = 8.4, P = 3.21
  AABCDEABCDEABEBEBEBEE
  RR4 : T = 11.4, E = 7.2, P = 3.08
  AAAABBBBCCDDEEEEBBEEE
  SPN : T = 9.0, E = 4.8, P = 2.14
  AAAACCDDBBBBBBEEEEEEE
  FB  : T = 12.2, E = 8.0, P = 3.34
  AABCDEAABBCDEEBBBEEEE
```

## Dificultades encontradas
Durante el desarrollo del programa, una de las principales dificultades fue la implementación de los algoritmos de planificación, especialmente el algoritmo de Feedback Multilevel Queue (FB). La complejidad radicó en el manejo de múltiples colas y en determinar correctamente en qué momento un proceso debía ser retirado de una cola y en cuál debía reinsertarse, considerando cambios de nivel, interrupciones y la llegada de nuevos procesos. Lo anterior, generó confusión en la lógica del flujo y el manejo del tiempo. Para solucionarlo, se organizó la simulación en etapas dentro del ciclo principal (llegadas, selección, ejecución y actualización), utilizando estructuras de datos como colas para gestionar los niveles de prioridad, y validando el comportamiento mediante múltiples ejecuciones con distintos conjuntos de procesos.

## Referencias.
[1] GeeksforGeeks. (2017, 22 de febrero). Program for FCFS CPU Scheduling | Set 1 - GeeksforGeeks. https://www.geeksforgeeks.org/operating-systems/program-for-fcfs-cpu-scheduling-set-1/

[2] GeeksforGeeks. (2018, 7 de septiembre). Round Robin Scheduling Algorithm with Different Arrival Time - GeeksforGeeks. https://www.geeksforgeeks.org/dsa/round-robin-scheduling-with-different-arrival-times/

[3] GeeksforGeeks. (2017b, 24 de febrero). Program for Shortest Job First (or SJF) CPU Scheduling | Set 1 (Non- preemptive) - GeeksforGeeks. https://www.geeksforgeeks.org/dsa/program-for-shortest-job-first-or-sjf-cpu-scheduling-set-1-non-preemptive/

[4] GeeksforGeeks. (2017, 5 de octubre). Multilevel Feedback Queue Scheduling (MLFQ) CPU Scheduling - GeeksforGeeks. https://www.geeksforgeeks.org/operating-systems/multilevel-feedback-queue-scheduling-mlfq-cpu-scheduling/

[5] GitHub - mds96589/CPU-Scheduling-Algorithms: An implementation of various CPU scheduling algorithms in C++. The algorithms included are First Come First Serve (FCFS), Round Robin (RR), Shortest Job First (SJF), Shortest Remaining Time Next (SRTN) and Feedback (FB). (s.f.). GitHub. https://github.com/mds96589/CPU-Scheduling-Algorithms?tab=readme-ov-file#feedback-fb
