Tarea 2 - MéridaFrancisco - QuezadaLeonardo
# PROBLEMA DE SANTA CLAUS

## Planteamiento:

- Santa está dormido en el polo norte.
- Sus 9 renos se encuentran de vacaciones.
- Un x número de elfos se encuentran haciendo juguetes.

## Reglas

- Si 3 elfos tienen problemas haciendo los juguetes, entonces despiertan a Santa para que les ayude.
- Si los 9 renos vuelven de sus vacaciones, despiertan a Santa para ir a repartir regalos.

# ENTORNO DE DESARROLLO

Realizamos lo solicitado en un programa desarrollado en python versión 3.12.3, llamado “T02.py” por lo que puede ser ejecutado en cualquier sistema operativo que cuente con Python3.

Se creó una interfaz del programa la cual fue desarrollada utilizando la biblioteca curses, está librería permite la creación de interfaces dinámicas en la terminal sin necesidad de entornos gráficos externos.

## Forma de ejecución

Para ejecutar, realizar la siguiente instrucción: :$ python3 T02.py

# ESTRATEGIA DE SINCRONIZACIÓN

Como estrategia de sincronización empleamos un mutex para acceder a variables compartidas, evitando condiciones de carrera. 

Además, utilizamos el patrón de “Señalización” para despertar a Santa en las situaciones que ameriten su atención. 

De forma que:
Un semáforo (“santaSem”) permite bloquear a Santa hasta que se junten 3 elfos o 9 renos
Un semáforo (“renoSem”) que bloquea a los renos hasta que santa termine de entregar regalos
Y un multiplex (“mutex_num_elfos”) que limita a que máximo 3 elfos puedan solicitar ayuda a la vez.

El funcionamiento es similar al de una barrera en el sentido de que se bloquean los hilos hasta que se cumple un cierto número en “espera”, sin embargo, para liberar el bloqueo es necesaria la ayuda de Santa en este caso.

## Comportamiento elfos
	
Duermen un tiempo aleatorio (simulan el tiempo que tardan en tener una duda)
Intentan acceder a la sección crítica controlada por el multiplex (“mutex_num_elfos”), lo que limita a un máximo de 3 en espera de ayuda.
Posteriormente intentan obtener el permiso de acceso a la variable contador por medio del mutex
Incrementa en uno el contador de elfos que piden ayuda
Si no se alcanzan los 3 elfos, nada más se libera el mutex
Si se alcanza los 3 elfos se despierta a santa con el semáforo “santaSem”
Los hilos quedan bloqueados hasta que santa los artienda
Una vez atendidos vuelven a su estado de trabajo (Vuelven a ser lanzados)

## Comportamiento renos

Duermen un tiempo aleatorio (tiempo en que están de vacaciones)
Al regresar intentan acceder al mutex para modificar la variable contador
Incrementa en uno el contador de renos que regresaron
Si no hay 9 renos, nada más se libera el mutex y el hilo queda bloqueado (renoSem bloqueado)
Si hay 9 renos, el último en llegar despierta a Santa mediante el semáforo “santaSem”.
Todos los renos quedan bloqueados esperando a que Santa termine de entregar regalos
Finalizando la entrega, Santa libera el semáforo “renoSem” para que estos puedan seguir su ejecución


## Comportamiento Santa

Santa está bloqueado (“dormido”) por medio del semáforo “santaSem”
Cuando recibe la señal de los renos o elfos, este despierta
Intenta acceder a la sección crítica del mutex para revisar el valor de los contadores (elfos y renos)
Si recibe la señal de los renos “contador_renos == 9”, entonces va a repartir regalos por un tiempo aleatorio, y al finalizar, libera a todos los renos (renoSem.release())
Si recibe la señal de los renos “contador_elfos == 3”, entonces va a repartir regalos por un tiempo aleatorio, y al finalizar, libera a todos los renos (renoSem.release())
Libera el mutex y vuelve a dormir
