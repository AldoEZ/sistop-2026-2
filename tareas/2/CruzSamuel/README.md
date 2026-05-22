 # Ejercicio de Sincronización: El Cruce del Río

## El problema que decidí resolver
Elegí el problema 6: El cruce del río. [cite_start]El planteamiento consiste en simular el cruce de un río en balsa para llegar a un encuentro de desarrolladores de sistemas operativos[cite: 136]. 
Las reglas establecidas en la presentación son:
- [cite_start]Los invitados son "hackers" (desarrolladores de Linux) y "serfs" (desarrolladores de Microsoft)[cite: 142].
- [cite_start]En la balsa caben exactamente cuatro personas. [cite_start]No pueden ir menos porque la balsa es demasiado ligera y volcaría[cite: 141].
- [cite_start]Para evitar peleas, el balance debe ser estricto: no pueden viajar 3 hackers y 1 serf, ni 3 serfs y 1 hacker[cite: 143, 144]. [cite_start]Las únicas combinaciones permitidas son 4 del mismo bando, o 2 y 2[cite: 145].
- [cite_start]Solo hay una balsa y está programada para volver sola, por lo que no hay que preocuparse por el viaje de regreso[cite: 146, 147].

## El lenguaje y entorno en que lo desarrollé
El programa fue desarrollado en **Python 3**. 
No utilicé ninguna biblioteca externa, únicamente las incluidas en la biblioteca estándar de Python para manejar la concurrencia: `threading`, `time`, `random` y `enum`.

### ¿Qué tengo que saber / tener / hacer para ejecutar su programa en mi computadora?
Solo es necesario tener Python 3 instalado. Para ejecutar la simulación, abre una terminal en el directorio donde guardaste el archivo y ejecuta:

```bash
python ProblemaBalsa.py
## La estrategia de sincronización (Mecanismo / Patrón)
Implementé una especie de patrón Monitor utilizando un Mutex (`threading.Lock`) acoplado a una Variable de Condición (`threading.Condition`).

- **Mutex:** Protege la sección crítica que son los contadores de personas esperando (`hackers_esperando`, `serfs_esperando`), el estado de la balsa y la formación del grupo.
- **Variable de condición (`wait` y `notify_all`):** La uso para dormir a los hilos que van llegando a la orilla si la balsa está llena o si todavía no completan un grupo válido. Cuando un hilo llega y se da cuenta de que su llegada completa un grupo permitido (ej. es el 4to Hacker), este mismo hilo asume la responsabilidad de "formar el grupo", cierra la balsa y hace un `notify_all()` para despertar a los demás.
- Hay un hilo independiente (`zarpar`) que simula el viaje de la balsa y resetea las variables para el siguiente viaje.

## Refinamientos implementados
Implementé dos refinamientos importantes para que el programa fuera más robusto:

- **Control de "Boletos" para evitar sobrecupo (Carrera de hilos):** Me di cuenta de que si tenía 6 hackers esperando y hacía un `notify_all()`, los 6 se despertaban de golpe y querían entrar a la balsa. Para evitar que se colaran, implementé variables de cuota (`allowed_hackers` y `allowed_serfs`). Cuando se forma un grupo, se "imprimen" exactamente los 4 lugares correspondientes. Así, cuando los hilos despiertan, solo los primeros que alcanzan a descontar esa variable logran subir; los demás se vuelven a dormir.
- **Finalización limpia (Graceful exit):** Muchas veces en estos problemas los hilos se quedan esperando eternamente si los totales no cuadran o al finalizar la simulación el programa se queda "colgado" esperando en un `join()`. Implementé un contador global (`personas_restantes`) y una bandera `finalizado`. Cuando el último hilo cruza, lanza un aviso general para que la balsa y cualquier remanente termine su ejecución de forma natural devolviendo el control a la terminal.

## Dudas y comentarios sobre la implementación
- **Mejora visual (Prints mezclados):** Noté que, aunque la lógica funciona bien, al imprimir en consola a veces los mensajes se pueden llegar a intercalar un poco rápido si varios hilos logran abordar en el mismo milisegundo. Pensé en meterle un Lock exclusivo para el `print`, pero creí que ya era sobrecomplicar la sincronización base y podría generar cuellos de botella innecesarios. ¿Es recomendable proteger las salidas a consola en este tipo de problemas?
- **Despertar en manada:** Aunque lo solucioné con mi validación de "boletos" (`allowed_hackers`), usar `notify_all()` hace que despierte a TODOS los hilos, incluso a los Serfs cuando a lo mejor el grupo que se formó era puro Hacker. Estuve investigando si se podían usar múltiples variables de condición (una para despertar solo hackers y otra para serfs), pero se volvía un poco espagueti el código. Creo que mi solución funciona bien, pero no sé si es la más óptima a nivel de uso de CPU.