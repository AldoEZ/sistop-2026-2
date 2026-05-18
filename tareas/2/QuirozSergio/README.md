# Tarea 2: Ejercicios de sincronización (Profesor y alumnos)

**Author:** Sergio Quiroz Salazar

## Instrucciones de ejecución
El programa está desarrollado en Python 3, por lo que no requiere compilación.

Para ejecutarlo desde la terminal de Linux:

    python3 asesor.py

El programa iniciará una simulación continua donde varios alumnos llegan aleatoriamente y son atendidos por un profesor.

---

## Breve explicación del diseño
El programa implementa una solución al problema de sincronización entre un profesor y varios alumnos, basado en el problema clásico del barbero dormilón.

Su funcionamiento se divide en las siguientes partes:

1. Sincronización principal:
   - Se utiliza un semáforo `alumnos` para indicar la cantidad de alumnos esperando.
   - El profesor permanece bloqueado (durmiendo) hasta que al menos un alumno llegue.

2. Exclusión mutua:
   - Se emplea un semáforo `mutex` para proteger el acceso a la cola y al diccionario de turnos.
   - Esto evita condiciones de carrera entre los hilos.

3. Control de turnos:
   - Cada alumno tiene su propio semáforo dentro del diccionario `turnos`.
   - El profesor despierta únicamente al alumno correspondiente, evitando wakeups incorrectos.

4. Cola FIFO:
   - Se utiliza una estructura `Queue` para mantener el orden de llegada de los alumnos.
   - Esto garantiza una atención justa y evita starvation.

5. Simulación:
   - Los alumnos llegan en tiempos aleatorios.
   - Cada alumno puede realizar entre 1 y 3 preguntas.
   - Se registran estadísticas de alumnos atendidos y rechazados.

---

## Ejemplo de ejecución

    Profesor: durmiendo...
    Alumno 2: llega
    Alumno 2: se sienta (en cola: 1)
    Profesor: atiende alumno 2 (en cola: 0)
    Alumno 2 realiza pregunta 1
    Alumno 2 realiza pregunta 2
    Profesor: terminó con alumno 2 (esperó 1.23s)

    Alumno 2: siendo atendido
    Alumno 2: se retira

---

## Dificultades encontradas y cómo se resolvieron

1. Sincronización incorrecta entre alumnos

   Dificultad: En implementaciones simples, varios alumnos podían ser despertados al mismo tiempo, generando condiciones de carrera.

   Solución: Se implementaron semáforos individuales por alumno (`turnos`), de modo que el profesor solo despierta al alumno correcto.

2. Protección de recursos compartidos

   Dificultad: El acceso concurrente a la cola y variables compartidas podía provocar inconsistencias.

   Solución: Se utilizó un semáforo `mutex` para garantizar exclusión mutua.

3. Evitar starvation

   Dificultad: Sin un orden definido, algunos alumnos podían no ser atendidos.

   Solución: Se utilizó una cola FIFO (`Queue`) para asegurar orden de llegada.

---

## Refinamientos implementados

- Uso de cola FIFO para garantizar equidad.
- Implementación de semáforos individuales por alumno.
- Simulación de múltiples preguntas por alumno.
- Registro de métricas del sistema (atendidos y rechazados).
