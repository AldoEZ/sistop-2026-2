# Tarea: Comparacion de planificadores

Sistemas Operativos, semestre 2026-2
Facultad de Ingenieria, UNAM
Alejandro Gutierrez Grimaldo


## Ejecucion

Se necesita Python 3 (lo probe con 3.11, pero deberia correr en cualquier version moderna). No hay dependencias externas.

```
python3 planificadores.py            
```

Cada ronda imprime:

1. La lista de procesos (nombre, llegada y duracion).
2. Para cada algoritmo: los promedios T (retorno), E (espera) y
   P (penalizacion T/t), y debajo la traza de ejecucion en ASCII.

## Algoritmos implementados

- **FCFS** (primero en llegar, primero en atenderse)
- **RR1** / **RR4** (round robin con cuanto 1 y 4)
- **SPN** (shortest process next, no expropiativo)
- **FB** (retroalimentacion multinivel, 4 niveles, cuanto 1)
- **SRR** (ronda egoista, con a=2 y b=1)


## Verificacion

La primera ronda del programa siempre usa el ejemplo de la tarea:

```
A: 0, t=3; B: 1, t=5; C: 3, t=2; D: 9, t=5; E: 12, t=5 (tot:20)
```


| Alg.  | T    | E    | P    | Traza                 |
|-------|------|------|------|-----------------------|
| FCFS  | 6.20 | 2.20 | 1.74 | AAABBBBBCCDDDDDEEEEE  |
| RR1   | 7.60 | 3.60 | 1.98 | ABABCABCBDBDEDEDEDEE  |
| RR4   | 7.20 | 3.20 | 1.88 | AAABBBBCCBDDDDEEEEDE  |
| SPN   | 5.60 | 1.60 | 1.32 | AAACCBBBBBDDDDDEEEEE  |

Ademas revise a mano:

- FCFS de la ronda 2 (A=0/7, B=0/2, C=2/3, D=3/3, E=3/7):  los tiempos de fin son 7, 9, 12, 15, 22 -> T promedio 11.4.
- SPN de la ronda 3 (A=0/7, B=4/2, C=8/5, D=8/2, E=8/3):  orden A, B, D, E, C -> traza AAAAAAABBDDEEECCCCC.

## Decisiones de implementacion

- En RR, cuando un proceso agota su cuanto y al mismo tiempo llega otro, el recien llegado entra a la cola **antes** de re-encolar al que acaba de correr. 
- En FB uso 4 niveles y cuanto 1 en todos. Los recien llegados entran al nivel 0 (mayor prioridad) y cada vez que les toca correr bajan un nivel hasta quedarse en el ultimo.
- En SPN, si hay empate en la duracion, gana el de llegada mas temprana.
- En SRR uso a=2 y b=1 (los nuevos ganan prioridad al doble de rapido que los aceptados). Cuando la cola de aceptados se vacia por completo, su prioridad se reinicia a 0.

## Nota

El semestre pasado ya habia cursado la materia y en aquella ocasion hice un proyecto muy parecido a este, por lo que parte de la logica general (como esta estructurado el programa, como se maneja la traza y el calculo de T, E y P) la reaproveche de esa version. La implementacion anterior tenia varias diferencias respecto a la que pide esta tarea, entre ellas que la prioridad se interpretaba "al reves" (ganaba el numero mas grande en vez del mas chico), asi que tuve que adaptar la logica de seleccion en varios algoritmos, ademas de reescribir las partes de FB y SRR para que cuadren con lo que pide el enunciado.

