#Tarea 3 - Comparación de planificadores
Integrantes:
-Espinosa González Sara Sofia
-Rosete Manzano Karina Lizeth

## Descripción del ejercicio resuelto
Para resolver el ejercicio, se analizaron distintos algoritmos de planificación bajo diferentes condiciones de trabajo, utilizando tanto un caso de referencia como múltiples escenarios con procesos generados de forma aleatoria. Esto permitió observar cómo las decisiones del planificador afectan el rendimiento del sistema según las características de los procesos.

Durante la resolución, se simuló el avance del tiempo y la ejecución de los procesos, lo que permitió visualizar su comportamiento y obtener resultados que facilitan la comparación entre algoritmos.

## Lenguaje y entorno
El programa lo desarrollamos en lenguaje **C**, utilizando únicamente librerías estándar como `stdio.h`, `stdlib.h` y `time.h`, por lo que no requiere dependencias externas. Se compiló y ejecutó desde la terminal utilizando el compilador GCC.

## Cómo compilar y ejecutar
Para ejecutar el programa, primero se debe compilar el archivo fuente:

1. Asegurarse de tener instalado un compilador de C (GCC).
2. Abrir una terminal y navegar hasta la carpeta donde se encuentra el archivo main.c.
3. Compila el programa con el siguiente comando: gcc comparador.c -o planificador
4. Esto generará un archivo ejecutable llamado planificador.
5. Para ejecutar el programa:
	- En Linux / Mac: ./planificador
	- En Windows (CMD o PowerShell): planificador.exe

Al ejecutarse, el programa primero muestra un caso de prueba fijo (para validar resultados) y posteriormente ejecuta varias rondas con procesos generados de forma aleatoria, aplicando todos los algoritmos de planificación implementados.

## Algoritmos implementados y funcionamiento
Se implementaron distintos algoritmos de planificación de procesos para simular la asignación del CPU:

- **FCFS:** este algoritmo ejecuta los procesos en orden de llegada, sin interrupciones.  
- **RR (Round Robin):** asigna el CPU por turnos usando un quantum (se probaron q=1 y q=4).  
- **SPN:** selecciona el proceso más corto entre los disponibles.  
- **FB:** utiliza múltiples colas de prioridad, degradando procesos que no terminan.  
- **SRR:** variante de RR que usa créditos para controlar la ejecución.

El simulador avanza en unidades de tiempo, incorporando procesos conforme llegan y seleccionando cuál ejecutar según el algoritmo. La ejecución se representa mediante un diagrama tipo Gantt, donde cada carácter indica el proceso activo en cada instante.

Al finalizar, se calculan métricas como tiempo de retorno, tiempo de espera y proporción de penalización para comparar el desempeño de los algoritmos.

## Verificación manual de resultados
Para comprobar la correcta implementación, se realizó una verificación manual de la Ronda 5 utilizando el algoritmo FCFS.

- Procesos:
A: llegada=0, t=6  
B: llegada=3, t=6  
C: llegada=6, t=6  
D: llegada=9, t=1  
E: llegada=11, t=8  

- Orden de ejecución (FCFS)
Como FCFS ejecuta por orden de llegada:
A → B → C → D → E

- Diagrama:
AAAAAABBBBBBCCCCCCDEEEEEEEE

- Cálculo de tiempos
A: fin = 6 → T = 6 - 0 = 6 → E = 0  
B: fin = 12 → T = 12 - 3 = 9 → E = 3  
C: fin = 18 → T = 18 - 6 = 12 → E = 6  
D: fin = 19 → T = 19 - 9 = 10 → E = 9  
E: fin = 27 → T = 27 - 11 = 16 → E = 8  

- Promedios
T = (6 + 9 + 12 + 10 + 16) / 5 = 10.60  
E = (0 + 3 + 6 + 9 + 8) / 5 = 5.20  
P = (1 + 1.5 + 2 + 10 + 2) / 5 = 3.30  

Estos valores coinciden con los resultados obtenidos por el programa, confirmando que la simulación es correcta.

## Resultados

A partir de las ejecuciones realizadas, se observó que el comportamiento de los algoritmos varía dependiendo de las características de los procesos.

En general:

- **SPN** tiende a obtener mejores tiempos promedio, ya que prioriza procesos cortos.
- **FCFS** es simple, pero puede generar tiempos de espera altos si llegan procesos largos primero.
- **RR** mejora la equidad entre procesos, aunque incrementa el tiempo de espera debido a los cambios de contexto.
- **FB y SRR** presentan un comportamiento más dinámico, ajustando la prioridad de los procesos y ofreciendo un balance entre eficiencia y equidad.

Además, al ejecutar múltiples rondas con datos aleatorios, se pudo observar que no existe un algoritmo óptimo en todos los casos, ya que el rendimiento depende directamente de la carga de trabajo.

---

## Problemas que tuvimos
Durante el desarrollo del programa surgieron varios retos:
- Implementar correctamente el manejo del tiempo y la llegada dinámica de procesos.
- Modelar adecuadamente las colas en algoritmos como Round Robin y Feedback.
- Evitar errores en la actualización del tiempo restante y el registro del tiempo de finalización.
- Manejar correctamente los momentos en los que el CPU queda inactivo.
- Implementar algoritmos más complejos como FB y SRR, ya que requieren múltiples estructuras y control de estados.

Estos problemas se resolvieron mediante pruebas iterativas, revisión manual de resultados y comparaciones con los ejemplos vistos en clase.













