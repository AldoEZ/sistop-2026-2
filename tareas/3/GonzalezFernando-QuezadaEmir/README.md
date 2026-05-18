# Tarea 3 - Comparación de planificadores

Integrantes:
- González Martínez Fernando
- Quezada Olivares Emir





## Algoritmos implementados

- **FCFS:** First Come, First Served: los procesos se atienden en el orden en que llegan, sin interrupciones.
- **RR1 / RR4:** Round Robin con quantum 1 y quantum 4. Cada proceso recibe una rodaja de tiempo fija; si no termina, vuelve al final de la cola.
- **SPN:** Shortest Process Next. De todos los que están esperando, siempre se elige el que tiene menor tiempo de servicio.
- **FB:** Feedback multinivel con 3 colas. Los procesos nuevos entran a la cola de mayor prioridad; si no terminan en su quantum, bajan de nivel.
- **SRR:** Selfish Round Robin. Maneja dos colas: una de "aceptados" y una de "nuevos". Los nuevos acumulan prioridad más rápido (`a=2`) que los aceptados (`b=1`), pero no pueden ejecutarse hasta que su prioridad alcance la mínima de los aceptados.

## Cómo se ven los resultados

```
- Ronda N:
  A: 3, t=5; B: 3, t=2; C: 4, t=4; D: 6, t=2; E: 6, t=3
    (tot:16)
  FCFS: T=9.0, E=5.8, P=3.27
    ...AAAAABBCCCCDDEEE
  RR1: T=10.6, E=7.4, P=3.27
    ...ABCABDECADECAECA
  RR4: T=10.4, E=7.2, P=3.39
    ...AAAABBCCCCDDEEEA
  SPN: T=7.2, E=4.0, P=2.12
    ...BBCCCCDDEEEAAAAA
  FB: T=10.6, E=7.4, P=3.31
    ...ABCDEABCDEACEACA
  SRR: T=9.8, E=6.6, P=3.45
    ...AAAAABCBDECDECEC
```

Los puntos (`.`) en el diagrama representan ciclos en los que el CPU no tiene nada que ejecutar.

## Métricas

Cada algoritmo reporta tres promedios calculados sobre todos los procesos de la ronda:

- **T** - Tiempo de retorno: desde que llega el proceso hasta que termina.
- **E** - Tiempo de espera: tiempo que el proceso pasó sin ejecutarse (`T - t_servicio`).
- **P** - Índice de penalización o retorno normalizado: `T / t_servicio`. Valores cercanos a 1 son ideales.

## Uso

No requiere dependencias externas.

```bash
python Codigo.py
```

Genera 5 rondas con cargas aleatorias de 5 procesos cada una. En caso de que se desee cambiar el número de rondas, se puede modificar el argumento en la última línea del archivo:

```python
ejecutar_simulacion(5)
```
Donde, en lugar de 5, puedes colocar el valor que se desee.
