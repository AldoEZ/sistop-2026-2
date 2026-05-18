# Tarea 3: Comparacion de planificadores

## Autores

- Ortega Ayala Fernando
- López Granados Derek André

## Problema elegido

Comparacion de planificadores de CPU bajo cargas aleatorias.

Se comparan:

- FCFS
- RR con quantum 1
- RR con quantum 4
- SPN
- FB de tres colas como refinamiento

## Lenguaje y entorno

- Lenguaje: Python 3
- Entorno probado: Python 3 en Linux
- No requiere paquetes externos

## Como ejecutar

Desde la raiz del repositorio:

```bash
python3 tareas/3/OrtegaFernando-LopezDerek/comparador_planificadores.py
```

Correrlo directo:

```bash
chmod +x tareas/3/OrtegaFernando-LopezDerek/comparador_planificadores.py
./tareas/3/OrtegaFernando-LopezDerek/comparador_planificadores.py
```

## Estrategia de comparacion

El programa genera cinco rondas aleatorias. En cada ronda crea una carga de procesos con llegadas escalonadas y tiempos de CPU distintos para mantener el sistema con presion suficiente.

Para cada ronda imprime:

- la carga generada
- los promedios de turnaround, espera y penalizacion
- una linea visual del calendario de ejecucion por algoritmo

Al final imprime un resumen con el promedio de todas las rondas.

## Nota sobre FB

FB se implementa como una retroalimentacion de tres colas con quantums 1, 2 y 4. Los procesos nuevos entran en la cola superior y, si no terminan, van bajando de nivel.

## Observaciones

- El orden de desempate es estable por orden de llegada y, si hace falta, por orden original de generacion.
- La salida cambia entre ejecuciones porque la carga se genera al vuelo.

## Conclusion

Con esta simulacion vimos que no hay un unico planificador mejor para todo: depende de lo que se quiera optimizar.

En estas pruebas, SPN suele dar los mejores tiempos promedio de espera y retorno, porque siempre atiende primero al proceso mas corto. Eso lo vuelve el mas eficiente en promedio, pero no siempre el mas justo, porque puede retrasar mucho a procesos largos.

FCFS es el mas facil de entender y de implementar, por eso es muy util didacticamente, aunque no suele aprovechar tan bien el procesador como SPN.

RR y FB son mas interesantes desde el punto de vista de justicia y respuesta del sistema. RR reparte mejor el tiempo entre procesos y FB agrega una idea mas realista de prioridades por niveles, aunque ambas politicas suelen sacrificar un poco la eficiencia promedio.

En general, la tarea sirvio para comparar de forma practica las politicas de planificacion y para ver que la eleccion depende del criterio que se quiera priorizar: simplicidad, justicia o eficiencia.
