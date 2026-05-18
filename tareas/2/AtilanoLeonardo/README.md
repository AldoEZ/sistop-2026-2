# Tarea 2: Ejercicios de Sincronización

**Alumno:** Atilano Leonardo

**Materia:** Sistemas Operativos

### El problema que decidí resolver
Elegí el problema 7 de las diapositivas: "El problema de Santa Claus".

### Entorno y cómo ejecutarlo
Lo programé en Python. Usé las bibliotecas `threading`, `time`, `random` y `curses` (para la interfaz visual).

**Para correrlo:** Es necesario ejecutarlo en una terminal de Linux (yo usé Ubuntu con WSL2) porque Windows nativo suele tener problemas con la biblioteca `curses`. 
Solo abrí la terminal y la ventana la hice un poco grande para que se muestre bien la ejecución, después se coloca el comando:
`python3 santa_claus.py`

### Estrategia de sincronización
Para resolverlo y que los hilos no chocaran, usé Semáforos y un Mutex (Lock):
- **Mutex (`candado_contador`):** Lo usé para proteger las variables globales que cuentan cuántos renos y elfos están esperando en la puerta. Si no bloqueaba esta parte, los contadores hacían cosas raras cuando varios hilos intentaban sumar al mismo tiempo.
- **Semáforos:** Usé tres (`sem_santa`, `sem_renos`, `sem_elfos`). Santa se queda bloqueado (durmiendo) en su semáforo. Solo se despierta cuando el reno número 9 o el tercer elfo le dan un `release()`.

### Refinamientos
Implementé la prioridad para los renos. 
Cuando Santa se despierta, el código revisa primero el contador de renos. Si ya están los 9, los atiende a ellos primero para ir a repartir regalos, ignorando temporalmente a los elfos aunque ya haya 3 formados esperando.

### Dudas y notas (Lo que me costó trabajo)
- Noté un detalle curioso visual: si imprimes un texto largo en `curses` y luego en esa misma coordenada pones un texto más corto, se quedan las últimas letras del mensaje viejo como "fantasmas" en la pantalla. Lo tuve que solucionar metiéndole espacios en blanco al final de los mensajes cortos para que limpiaran el renglón.
