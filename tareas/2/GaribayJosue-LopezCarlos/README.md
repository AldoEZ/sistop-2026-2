# Tarea 2. Ejercicios de sincronización 
Universidad Nacional Autónoma de México 
Facultad de Ingeniería  
Sistemas Operativos 
Alumnos: 
- Garibay Zamorano Josué Benjamín 
- López López Carlos Daniel 
Fecha de entrega: 26/03/26 

## Problema 3. El elevador 

En este caso nosotros decidimos elegir el problema número tres, el cual es el problema del elevador, estábamos indecisos entre este y el de "Gatos y Ratones" debido a que ambos se nos hacían divertidos e interesantes, al final nos decidimos por el problema de el "Elevador", debido a temas de tiempo que tuvimos en la semana además de que se nos hacia un poco más sencillo el solucionar el refinamiento solicitado en este problema que el de otros problemas propuestos, pero si hay tiempo quizás revisemos el de "Gatos y Ratones" en semana santa :D. 
Este ejercicio nos dice que en la facultad existe un problema, el elevador de la facultad se descompone de manera seguida, todo esto debido a que sus alumnos y maestros no respetan el limite de usuarios que caben dentro del elevador al mismo tiempo. 
Dicho limite es de 5 personas, así mismo la cantidad de pisos que va a recorrer el elevador es de 5 pisos, donde un usuarios puede llamar al elevador en cualquier piso para ir a cualquier otro. 
Se nos indica que podemos: 
* Implementar al elevador como un hilo y a los usuarios como otro hilo externo. 
Así mismo se nos dice que para ir de un piso a otro el elevador debe de recorrer todos los pisos, y que los usuarios prefieren esperar dentro del elevador que afuera, esto es, si yo quiero ir del piso 3 al piso 1, pero este va de subida hasta el piso 5 yo prefiero subir hasta el piso 5 y bajar todos los pisos que esperarme a que el elevador vaya de bajada y bajar solo tres pisos. 
El refinamiento para este problema es como podemos evitar la inanición, es decir ¿Cómo podemos evitar que un grupo de alumnos que van entre pisos monopolicen al elevador y dejen fuera a un usuario que va a un piso distinto?, esto es, si un grupo de alumnos van del piso 2 al piso 3, y otro grupo va del piso 3 al piso 2 y así sucesivamente, ¿Cómo evito que los alumnos monopolicen al elevador y dejen fuera a un usuario que quizás vaya del piso 1 al piso 5? 

## Lenguaje y requerimientos de ejecución 
Todo lo anterior mencionado es el planteamiento del problema, ahora bien ¿Cómo le vamos a dar solución?, bueno para esto nos apoyaremos de el lenguaje de programación Python, pues es el que hemos venido utilizando en todas las clases, por lo que nos sentimos un poco más familiarizados con el y con los ejemplos vistos en clase, tales como el problema de "El Servidor Web". 
Así mismo utilizaremos "curses" en Python, nosotros al principio estuvimos trabajando en una maquina virtual con Linux por lo que no fue necesario descargar nada, ya que en Linux curses viene por defecto, pero en el caso de Windows al momento de trabajar en Visual Studio tuvimos problemas, pues curses no viene por defecto, por lo que tuvimos que ejecutar la siguiente línea de código en nuestra terminal, para poder ver el funcionamiento de nuestro programa: 
``` bash pip install windows-curses  
```  
En caso de ver el funcionamiento en Linux o ya tener instalada la biblioteca en Windows se puede omitir este paso. 

Una vez listo el entorno ya sea que trabajemos en Linux o Windows, nos posicionamos en la dirección de nuestro archivo y ejecutamos el siguiente comando: 
``` bash $ python elevador.py
```
En caso de haber guardado el programa con otro nombre se sustituye el nombre propuesto por el nombre del archivo guardado. 

## Estrategia de sincronización 

Para este problema utilizamos variables de condición, los cuales trabajan de la mano con los MUTEX (Mutual Exclusion), específicamente trabajamos con .wait() , con el cual adquiríamos el "candado" o mejor dicho permiso para poder entrar al elevador. 
Así mismo usamos el concepto de Monitor, el cual nos ayudo a encapsular datos en una clase y evitar que estos se corrompan. 

## Refinamientos 

Para el problema del elevador el refinamiento nos solicitaba evitar la inanición, en donde el elevador se quedara atrapado entre dos pisos. 
Sobre si lo resolvimos la respuesta corta es que sí, si lo intentamos resolver y creemos haberlo resuelto, pero en nuestra resolución estamos dudosos, por no decir poco convencidos, pues lo que realizamos fue obligar al elevador a completar su trayectoria, es decir que si sube termine de subir para entonces comenzar a bajar, pero entonces ¿Qué pasa cuando un usuario sube en el piso 2 y va para el piso 1 si no hay más gente esperando el elevado en pisos superiores?, pues tendrá que subir hasta el último piso y bajar de nueva cuenta, es poco eficiente, pero es la única manera que encontramos de darle solución. 

## Dudas y Comentarios 

Fuera de nuestra duda sobre si la implementación del refinamiento fue la correcta, creemos no tener dudas acerca de la implementación del problema. 
Sobre la implementación en código nuestra mayor complicación fue curses, pues es algo que no habíamos utilizado antes y dado el trabajo de la facultad no teníamos mucho tiempo para volvernos expertos en su uso, si bien si consultamos fuentes de información para su implementación, así mismo debemos ser honestos y admitir el uso de modelos grandes de lenguaje (LLM's) los cuales usamos específicamente para entender como usar curses para la resolución del ejercicio. 