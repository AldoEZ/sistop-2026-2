# Tarea 02. Problema de sincronización: El elevador.
**Fecha de entrega:** 26/03/26.

### Integrantes:
- Estrada Zacarias Aldo Axel
- Sánchez Salazar Jazmín

## Problema: El elevador.
Se tiene un elevador que atiende 5 pisos y se descompone demasiado porque los que lo usan no respetan los límites lo que ocasiona que se desgaste.
Se tiene que implementar el elevador como un hilo y cada persona que quiera usarlo como un hilo también.
Las personas que quieran usarlo pueden llamarlo desde cualquier piso y puede querer ir a cualquiera de los 5 pisos. 
El elevador cuenta con una capacidad máxima de 5 pasajeros considerando un peso por persona constante. Si el usuario quiere ir de un piso a otro debe pasar por los pisos intermedios, además de que los usuarios prefieren esperar dentro del elevador que fuera de él.

## Lenguaje y entorno en el que se desarrolló: Python en Windows.
- ¿Qué hay que saber/tener para ejecutar el programa en alguna computadora?

Dado que el programa se desarrolló en VScode puede ejecutarse desde cualquier terminal, ya sea PowerShell, cmd, o para la entrega de las tareas desde el Git Bash, siempre y cuando cuente con Pyhton 3 instalado. Para ejecutarlo se puede utilizar lo siguiente independientemente del entorno de desarrollo:
```bash
python elevador.py
```
## La estrategia de sincronización (mecanismo/patrón)empleada para lograrlo.
Para resolver el problema se utilizaron distintos mecanismos de sincronización, combinando varios patrones de concurrencia que se explican a continuación:
### Mutex
Se utilizó un `Lock` (`lock_elevador`) para garantizar exclusión mutua al acceder a recursos compartidos, tales como: lista de pasajeros, solicitudes por piso y el estado del elevador (piso actual, dirección, puertas).

Este mecanismo evita condiciones de carrera (race conditions) entre los distintos hilos.
### Multiplex para el control de acceso
Se utilizó un semáforo (`BoundedSemaphore`) para modelar la capacidad máxima del elevador.
Se inicializó con el valor de la capacidad (5) personas, para el pasajero que adquiere el semáforo al intentar subir, además si el elevador está lleno, el hilo espera hasta que se libere espacio garantizando que nunca se exceda el límite de pasajeros permitido.

### Señalización
Por medio de un (`threading.Condition`) se coordinó la interacción entre hilos, como (`condicion_subida`) para dejar que los usuarios esperen a que el elevador llegue a su piso y abra puertas o (`condicion_movimiento`) para dejar que los pasajeros esperen hasta llegar a su destino, la señalización se hace con un (`notify_all`) que notifica cuando el elevador cambia de estado.

### Cola
Se implementó con la matriz de (`solicitudes_por_piso`) funcionando como una colección de colas por piso, donde por cada piso se guardan los identificadores (id's) de las personas que hacen una solicitud al elevador, facilitando la gestión concurrente de múltiples solicitudes.

## Refinamiento empleado.
Uno de los problemas del ejercicio es la inanición, cómo podemos asegurar que una serie de alumnos que van entre dos pisos no monopolicen al elevador ante otro usuario que va a otro piso, es decir, cómo evitar que el elevador permanezca en unos cuantos pisos dejando de lado los demás pisos. 
Por lo anterior, es que se implementó el control de movimientos marcando un límite máximo de movimientos(`max_mov`), que fueron 5 movimientos en nuestra implementación, los cuáles se contabilizaron con un contador de movimientos (mov_misma_dirección), si el elvador alcanza los 5 movimientos en la misma dirección cambia su dirección permitiendo que así pueda atender los demás pisos. 

## Notas.
En el caso de la resolución de la inanción aún nos quedan dudas respecto a: a pesar de que el elevador cambie de dirección y pase a los demás pisos puede suceder lo mismo de quedarse entre dos pisos intermedios hasta llegar a los demás pisos por lo que los usuarios de los demás pisos sí podrán acceder al elevador porque el máximo de movimientos para cambiar de dirección existe, pero podrían esperar mucho tiempo, ya que no hay un límite tiempo de espera. 
En principio se intentó resolver con la prioridad de antigüedad para decidir quien había subido primero tenía derecho a bajar primero, pero lo cambiamos por el límite de movimientos en una sóla dirección para garantizar el correcto funcionamiento del elevador bajo condiciones de concurrencia. No obstante, creemos que algo bien implementado incluyendo la prioridad, el máximo de movimientos en una sóla dirección y el tiempo de espera podría garantizar el correcto funcionamiento del elevador evitando la inanición por completo lo cuál podría ser muy efectivo para resolver por completo el problema. 