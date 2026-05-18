Problema resuelto
Se decidió resolver el problema de “Los alumnos y el asesor”.

En este problema existe un asesor que atiende dudas de varios alumnos.
El asesor cuenta con un número limitado de sillas para que los alumnos esperen su turno. 
Si no hay alumnos, el asesor se duerme. Cuando llega un alumno, si hay sillas disponibles, se sienta y espera. Si no hay sillas libres, el alumno se retira y vuelve después. 
El asesor solo puede atender a un alumno a la vez.

Lenguaje y entorno de desarrollo
El programa fue desarrollado en Python, utilizando la biblioteca threading para simular concurrencia mediante hilos.

Para ejecutar el programa se necesita:
- Tener Python 3 instalado
- Guardar el archivo con nombre: alumnos_asesor.py
- Ejecutarlo desde una terminal con el comando:

  python3 alumnos_asesor.py


Estrategia de sincronización
Se utilizó una estrategia basada en semáforos y un lock (mutex).

Mecanismos empleados:
- Semaphore alumnos_esperando:
  Indica cuántos alumnos están esperando ser atendidos.
  El asesor se bloquea aquí cuando no hay nadie.
- Semaphore asesor_listo:
  Sirve para coordinar el momento en que un alumno pasa a ser atendido.
- Lock mutex:
  Protege las variables compartidas, principalmente:
  - el número de sillas disponibles
  - la cola de alumnos esperando

Funcionamiento general:
1. El asesor inicia en espera.
2. Cuando un alumno llega, revisa si hay silla disponible.
3. Si hay lugar, se sienta, se forma y despierta al asesor.
4. El asesor toma a un alumno de la cola y lo atiende.
5. Solo un alumno puede ser atendido a la vez.
6. Cuando no hay alumnos, el asesor vuelve a dormir.

Comentarios
La simulación utiliza tiempos aleatorios para representar la llegada de los alumnos y el tiempo que dura cada asesoría. Además, cada alumno puede hacer entre 1 y 3 preguntas, regresando en distintos momentos para volver a intentar ser atendido.