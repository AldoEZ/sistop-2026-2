# Tarea 2: Ejercicios de sincronización
**Problema a resolver:** De gatos y ratones

**Integrantes:**
* González Martínez Fernando 
* Quezada Olivares Emir

## Lenguaje de Programación (Python3)
El código fue realizado en Python puro (específicamente compatible con la versión 3). Decidimos utilizarlo pues el lenguaje estándar que el profesor utiliza para los ejemplos en clase, además de otras ventajas que trae, como su sintaxis limpia y la lógica de los semáforos sin la complejidad de manejo de memoria que tendríamos en C o C++.

## Entorno y Librerías
Lo mejor de este código es que no requiere instalar nada externo. Utiliza módulos que ya vienen integrados en la librería estándar de Python:

* threading: Proporciona la clase Thread y la primitiva Semaphore.
* time: Se usa para el time.sleep(), que es vital para "simular" que el tiempo pasa mientras comen.
* random: Para que cada ejecución sea distinta, dándoles a los hilos tiempos de espera aleatorios.

## ¿Dónde y cómo ejecutarlo?
Cualquier entorno que soporte Python 3 funcionará de maravilla. Algunas de las opciones más comunes:
* VSCode
* Terminal: Simplemente guardar el archivo con extensión .py (por ejemplo: gatosRatones.py) y correr el comando:
python gatosRatones.py (o python3 gatosRatones.py dependiendo del sistema).

## Estrategia

Para resolver este problema utilizamos tres mecanismos principales de sincronización para garantizar la integridad de los datos y la justicia en el acceso a los recursos.

1. Semáforos de Recurso (Counting Semaphores)

Utilizamos un semáforo contador para gestionar el depósito de platos (NUMERO_PLATOS).

    Función: Limitar físicamente la cantidad de hilos (gatos o ratones) que pueden estar "comiendo" simultáneamente, actuando como un limitador de capacidad para la sección crítica.


2. Mutex (Exclusión Mutua)

Para proteger las variables globales y los contadores (ratonesComiendo, gatosComiendo, ratonesRIP), empleamos semáforos binarios o Mutex.

    El primer miembro de un bando (ej. el primer ratón) bloquea el acceso al bando contrario, y solo el último miembro en salir libera dicho bloqueo. 

3. Torniquete

Para evitar la inanición (starvation) de los gatos, se ha implementado un Torniquete.

    Si los ratones llegan en un flujo constante, los gatos podrían quedarse esperando indefinidamente (inanición).

    El torniquete obliga a los hilos a pasar por una "puerta" de uno en uno. Si un gato se detiene a esperar que los ratones salgan de la sala, el torniquete se bloquea, impidiendo que nuevos ratones sigan entrando y permitiendo que los gatos tomen su turno una vez que la sala quede vacía.


