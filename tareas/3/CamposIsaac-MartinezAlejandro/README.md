# MPDP - Algoritmos de Planificación de Procesos

**Curso:** Sistemas Operativos  
**Tarea 3:** Comparación de Planificadores  
**Autores:**  
- Campos Isaac  
- Martinez Alejandro  

---

## Descripción

Este programa implementa seis algoritmos de planificación de procesos:

- **FCFS** (First Come First Served)
- **Round Robin** con quantum = 1 y quantum = 4
- **SPN** (Shortest Process Next)
- **FB** (Retroalimentación multinivel)
- **SRR** (Selfish Round Robin)

Al ejecutarlo, se muestra un menú interactivo donde se elige el algoritmo, se genera un conjunto aleatorio de procesos y se imprime:

- La línea de tiempo de ejecución.
- Las métricas por proceso (Tiempo total, Espera, Penalty).
- Los promedios de cada métrica.

---

## Cómo ejecutar

Es necesario tener Python 3 instalado. Luego, en la terminal:

```bash
python3 MPDP.py

## Cambiar parámetros de simulación

Todos los parámetros (número de procesos, rangos de tiempo y llegada, quantums, etc.) están definidos al inicio del código.  
Para modificarlos, abrir el archivo MPDP.py y editar las constantes en la sección "CONFIGURACION GENERAL" y las secciones específicas de cada algoritmo.

## Nota

Los procesos se generan aleatoriamente cada vez que se ejecuta un algoritmo, por lo que los resultados pueden variar entre ejecuciones.
