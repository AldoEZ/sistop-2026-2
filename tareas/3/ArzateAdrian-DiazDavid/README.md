# Tarea 3: Comparación de Planificadores

**Autores:** Adrián Arzate (**AxlBoy11th**) y David Díaz (**Cuervy117**)

## Descripción

En esta tarea implementamos un simulador para comparar distintos algoritmos de planificación de procesos. El programa genera cargas aleatorias de trabajo y evalúa el comportamiento de varios planificadores sobre la misma carga, para poder comparar sus resultados de manera justa.

Los algoritmos implementados son:

- **FCFS** (*First Come, First Served*)
- **RR** (*Round Robin*, con **quantum = 1**)
- **SPN** (*Shortest Process Next*)
- **FB** (*Feedback*, con **3 colas** y **quantum = 1**)

Para cada ronda se generan **5 procesos aleatorios**, cada uno con:

- un **nombre** (`A`, `B`, `C`, ...)
- un **tiempo de llegada** entre `0` y `10`
- un **tiempo de servicio** entre `1` y `5`

Después, cada algoritmo ejecuta esa misma carga y se calculan las siguientes métricas promedio:

- **T**: tiempo de retorno
- **E**: tiempo de espera
- **P**: penalización, calculada como `T / tiempo_servicio`

Además, se imprime una **secuencia de ejecución** para visualizar cómo fue atendido cada proceso a lo largo del tiempo.

## Estructura general del programa

El programa está organizado alrededor de una clase `Proceso`, definida con `@dataclass`, que almacena:

- nombre del proceso
- tiempo de llegada
- tiempo de servicio
- tiempo restante
- tiempo de retorno
- tiempo de espera

### Generación de procesos

La función `proceso_aleatorio(num_procesos)` genera una lista de procesos aleatorios y la ordena por tiempo de llegada.

### Algoritmos implementados

#### FCFS

Ejecuta los procesos en el orden en que llegan. No hay expulsión: cuando un proceso comienza, termina por completo antes de que se atienda al siguiente.

#### RR

Usa una cola de listos y asigna CPU por turnos con un **quantum de 1**. Si un proceso no termina en su turno, vuelve al final de la cola.

#### SPN

Selecciona, entre los procesos listos, el que tenga el menor tiempo de servicio. Es una política no expulsiva.

#### FB

Implementa una realimentación con múltiples colas. Todos los procesos entran primero a la cola de mayor prioridad, y si consumen su quantum sin terminar, bajan de nivel.

## Métricas calculadas

Para cada proceso terminado se calculan:

- **Tiempo de retorno**  
  `retorno = tiempo_finalizacion - tiempo_llegada`

- **Tiempo de espera**  
  `espera = retorno - tiempo_servicio`

- **Penalización**  
  `penalizacion = retorno / tiempo_servicio`

Luego se reporta el promedio de cada valor para todos los procesos de una ronda.

## Formato de salida

En cada ronda, el programa imprime:

1. La lista de procesos generados, con su tiempo de llegada y servicio
2. El tiempo total de CPU requerido
3. Los resultados de cada algoritmo:
   - `T`
   - `E`
   - `P`
   - secuencia de ejecución

En la secuencia:

- cada letra representa el proceso ejecutado en ese instante
- `-` representa CPU ociosa

## Requisitos

- Python 3

No se usan librerías externas; únicamente módulos estándar de Python.

## Instrucciones de ejecución

Guarda el archivo del programa y ejecútalo desde la terminal.

## Ejemplo de ejecución
```text
- Ronda 1:
  C: 0, t=1; A: 2, t=3; B: 7, t=4; E: 7, t=3; D: 9, t=2 (tot:13)
  FCFS: T=4.40, E=1.80, P=1.77
  C-AAA--BBBBEEEDD
  RR: T=5.20, E=2.60, P=1.92
  C-AAA--BEBEDBEDB
  SPN: T=3.80, E=1.20, P=1.35
  C-AAA--EEEDDBBBB
  FB: T=5.00, E=2.40, P=1.78
  C-AAA--BEDBEDBEB
- Ronda 2:
  C: 1, t=5; A: 2, t=2; D: 2, t=5; B: 5, t=1; E: 8, t=5 (tot:18)
  FCFS: T=8.40, E=4.80, P=3.48
  -CCCCCAADDDDDBEEEEE
  RR: T=9.20, E=5.60, P=2.78
  -CCADCADBCDECDEDEEE
  SPN: T=7.40, E=3.80, P=2.22
  -CCCCCBAADDDDDEEEEE
  FB: T=9.80, E=6.20, P=2.42
  -CADCBADEECDECDECDE
- Ronda 3:
  D: 1, t=4; A: 2, t=1; B: 6, t=1; C: 6, t=1; E: 6, t=3 (tot:10)
  FCFS: T=3.20, E=1.20, P=1.93
  -DDDDABCEEE
  RR: T=3.00, E=1.00, P=1.58
  -DDADDBCEEE
  SPN: T=3.20, E=1.20, P=1.93
  -DDDDABCEEE
  FB: T=2.80, E=0.80, P=1.38
  -DADDDBCEEE
- Ronda 4:
  D: 1, t=5; E: 4, t=3; B: 6, t=4; A: 10, t=3; C: 10, t=2 (tot:17)
  FCFS: T=6.20, E=2.80, P=2.08
  -DDDDDEEEBBBBAAACC
  RR: T=7.40, E=4.00, P=2.32
  -DDDDEDEBEBACBACBA
  SPN: T=6.00, E=2.60, P=1.92
  -DDDDDEEEBBBBCCAAA
  FB: T=8.80, E=5.40, P=2.47
  -DDDEEBBDEACACBDAB
```

## Comentarios finales

A partir de las pruebas realizadas, observamos que:

- **FCFS** es el algoritmo más simple y fácil de seguir, pero puede perjudicar a procesos cortos si llegan detrás de procesos largos.
- **RR** reparte mejor el uso del procesador entre procesos, aunque puede incrementar el tiempo de espera promedio.
- **SPN** suele ofrecer mejores resultados en espera y retorno cuando hay procesos cortos disponibles, aunque favorece ese tipo de cargas.
- **FB** introduce un comportamiento más dinámico al mover procesos entre colas según su uso de CPU, buscando balancear prioridad y justicia.

En general, la comparación permite ver que no existe un único algoritmo óptimo para todos los casos: el rendimiento depende de la carga generada y del criterio con el que se quiera favorecer a los procesos.