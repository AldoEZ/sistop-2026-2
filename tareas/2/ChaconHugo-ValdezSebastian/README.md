# Ejercicio de Sincronización

## Los alumnos y el asesor

### Planteamiento
Un profesor de la facultad asesora a varios estudiantes, y estamos
en su horario de atención.

### Reglas 
* Un profesor tiene *__x__* sillas en su cubículo
    * Cuando no hay alumnos que atender, las sillas sirven como
sofá, y el profesor se acuesta a dormir la siesta.

* Los alumnos pueden tocar a su puerta en cualquier momento,
pero no pueden entrar más de *__x__* alumnos

* Para evitar confundir al profesor, sólo un alumno puede
presentar su duda (y esperar a su respuesta) al mismo tiempo.
    * Los demás alumnos sentados deben esperar pacientemente su
turno.
    * Cada alumno puede preguntar desde 1 y hasta *__y__* preguntas
(permitiendo que los demás alumnos pregunten entre una y
otra)



## Lenguaje y entorno

Para resolver el problema usamos python, con las siguientes bibliotecas:
* threading: Para crear procesos paralelos
* time: Para poder coordinarlos
* random: Para crear caos y entre estos y que el programa tenga algo que resolver 

### Requisitos
* Python 3 instalado
* Cualquier sistema operativo 

### Cómo ejecutar el programa

1. Abrir una terminal.
2. Navegar a la carpeta donde se encuentra el archivo `asesor.py`.

```bash
cd ruta/de/la/carpeta
```
3. Ejecutar programa:

```bash
python3 asesor.py
```



## Estrategia de sincronización

Para resolver el problema utilizamos una combinación de exclusión mutua y sincronización condicional usando semaforos semáforos:

* mutex (Binary Semaphore): Lo usamos para garantizar que haya exclusion mutua al intentar acceder a la variable global sillas_disponibles. Esto evita condiciones de carrera cuando múltiples hilos de alumnos intentan sentarse o cuando el asesor libera una silla simultáneamente.

* alumnos_esperando (Counting Semaphore): Funciona como una especie de aviso para el asesor. Inicializado en 0, bloquea al hilo del asesor hasta que un alumno realiza un release(), indicando que hay alguien que requiere atención.

* asesor_disponible (Binary Semaphore): Hace que se pueda sincronizar el momento exacto de la asesoría. El alumno se bloquea tras sentarse hasta que el asesor le da paso, asegurando que solo un alumno sea atendido a la vez.



## Refinamiento

El principal refinamiento que hicimos fue poner los resultados en una tabla para que se viera mas estetico y sea mas sencillo de leer que esta sucediendo

Otro fue crear una interrupcion con el teclado _KeyboardInterrupt_, de esta forma podemos parar el programa rapidamente 



## Dudas / mejoras
No logramos que sirviera la idea de que la tabla se actualizara en tiempo real, en vez de imprimir infinitamente.



## Autores

Chacon Hugo

Valdez Sebastian

Materia: **Sistemas Operativos**
Semestre: **2026-2**