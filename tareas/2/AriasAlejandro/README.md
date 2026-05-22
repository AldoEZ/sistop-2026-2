# El cruce del río

Para la tarea 2, elegí el problema del cruce del río, que consiste en lo siguiente:

Hay un encuentro de desarrolladores de sistemas operativos, pero para llegar a este se necesita cruzar un río en una balsa.
Esta balsa es muy ligera y por eso se necesita que exactamente 4 personas la aborden.
Al encuentro se invitaron hackers y serfs, pero estos se pelean entre sí si existe un número impar de ellos en la balsa, por lo que se deben de organizar en pares o en grupos de 4 del mismo bando.
Solo hay una balsa y esta regresa sola.

---

## Ejecución

Para ejecutar el programa, se necesita tener instalado **Python 3** y encontrarse en un ordenador con **Sistema Operativo Linux**.

Su ejecución se realiza con el siguiente comando, sobre el directorio en donde se encuentra Turtle:

```bash
python3 Cruce.py
```
---

## Estrategias de sincronización

Para resolver este problema y, como lo indiqué de manera breve en la cabecera de mi código, utilicé tanto primitivas de sincronización como patrones basados en semáforos.

Debido a que se indica que se necesitan 4 personas exactamente para poder utilizar la balsa, hice uso de una barrera reutilizable, esto me obliga a que 4 hilos se sincronicen para poder continuar.

También hice uso de un mutex para poder controlar contadores compartidos con el fin de poder manipular la barrera. Esto también me es útil para poder manipular colas.

Las colas por su parte, las utilicé para poder generalizar a los hackers y a los serfs y evitar que estén a sus anchas intentando abordar la balsa en grupos que no son válidos (Para la seguridad de estos y evitar que la balsa se vuelque 🫠).

Como también lo mencioné en el código, a veces se creaba una segunda o hasta tercera balsa (Parece que algunos hackers y serfs se volvieron amigos y construyeron su propia balsa para poder cruzar). Esto es un problema según la definición del problema y es lo que me lleva a la última primitiva de sincronización que utilicé.

La balsa sigue la definición de un semáforo, en la que todos los hilos tienen que esperar hasta que esta regrese y puedan abordar nuevos pasajeros a la balsa y poder cruzar antes de repetir el proceso.

---

## Uso básico

Este programa necesita de dos números enteros para poder simular a las personas, por lo que ambos tienen que ser pares y tienen que sumar un múltiplo de 4 entre sí; es decir; el total de personas solo puede ser múltiplo de 4.


---

### Ejemplo de ejecución
```bash
python3 Cruce.py
Ingrese el número de hackers: 4

Ingrese el número de serfs: 4

Iniciando el cruce del río...

Hacker está esperando para abordar...
Hacker está esperando para abordar...
Serf está esperando para abordar...
Serf está esperando para abordar...

Iniciando abordaje...

Todos han abordado, balsa zarpando...

La balsa llegó a la otra orilla :D

La balsa regresó al muelle.

Hacker está esperando para abordar...
Hacker está esperando para abordar...
Serf está esperando para abordar...
Serf está esperando para abordar...

Iniciando abordaje...

Todos han abordado, balsa zarpando...

La balsa llegó a la otra orilla :D

La balsa regresó al muelle.

Todos han cruzado el río exitosamente
```
