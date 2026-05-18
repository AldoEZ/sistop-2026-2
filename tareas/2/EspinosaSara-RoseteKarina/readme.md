# Ejercicio de sincronización: Alumnos y asesor

Autores: Espinosa Gonzalez Sara Sofia y Rosete Manzano Karina Lizeth

## Problema que se decidió resolver
Para esta tarea escogimos el problema de “Los alumnos y el asesor”. La idea es simular a un profesor que atiende alumnos en su cubículo, pero con ciertas restricciones. Hay un número limitado de sillas, entonces no todos pueden entrar al mismo tiempo y solo puede atender a un alumno a la vez mientras los demás esperan. Si no hay alumnos, el profesor se queda esperando hasta que llega alguien. El objetivo fue modelar esto con hilos y sincronización, evitando errores como que dos alumnos sean atendidos al mismo tiempo, lo cual nos pasó al inicio.

## Lenguaje y entorno
Usamos Python 3 con librerías basicas: threading, time, random y argparse. No usamos nada externo. Lo corrimos en Git Bash y también en la terminal normal, y en ambos funcionó sin problema.

## Cómo ejecutar
Desde la terminal:
python3 alumnos_asesor.py
Tambien se pueden cambiar parametros:
python3 alumnos_asesor.py --students 10 --chairs 3 --max-questions 4 --seed 1
La verdad si ayuda cambiar estos valores porque se ve distinto el comportamiento.

## Estrategia de sincronización
Nos basamos en el problema del “sleeping barber”, pero adaptado. Usamos un semaforo para las sillas, otro para avisar que hay alumnos, un lock para proteger variables y threads para cada alumno. Al inicio no usamos bien el lock y nos pasó que dos alumnos hablaban con el profesor al mismo tiempo, entonces tuvimos que corregir eso.

## Cómo funciona el programa
Los alumnos llegan en tiempos aleatorios. Cuando llegan: si hay silla se quedan, si no hay se van. El profesor si no hay nadie espera, y si hay alumnos atiende uno por uno. Cada alumno puede hacer varias preguntas, pero no seguidas siempre, o sea no monopoliza al profesor. Los que están esperando se quedan sentados hasta que les toca.

## Detalles de sincronización
Aqui fue donde mas nos atoramos. Tuvimos que asegurar que no entren mas alumnos que sillas, que solo uno sea atendido a la vez y que no haya acceso simultaneo a variables compartidas. El mutex fue clave porque sin eso se rompia todo. No hicimos una cola formal, pero si funciona bien el orden.

## Refinamientos
Le agregamos llegadas aleatorias, tiempo de atencion variable, numero de preguntas distinto por alumno y parametros desde la terminal. Tambien usamos seed para poder repetir pruebas porque luego era dificil ver si ya funcionaba o no.

## Resultados
Se observa que el profesor espera cuando no hay alumnos, los alumnos ocupan sillas, algunos se van si no hay espacio y la atencion es de uno en uno. La salida cambia cada vez, pero eso es normal por los threads.

## Problemas que tuvimos
Al inicio tuvimos varios errores: dos alumnos siendo atendidos al mismo tiempo, variables compartidas sin proteccion y orden raro en la ejecucion. Lo fuimos arreglando con locks y reorganizando los semaforos. Tambien nos costó entender bien cuando usar cada semaforo, no fue tan directo al inicio.
