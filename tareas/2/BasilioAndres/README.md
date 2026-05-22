# Tarea 2: Ejercicios de Sincronización
**Alumno:** Andrés Basilio (BassAndres)

## Problema resuelto
Decidí resolver el problema de **Gatos y Ratones** ya que le encontré un parecido muy interesante con el problema de Los Filósofos Comensales (por el tema de compartir recursos limitados y evitar que se coman entre ellos jaja) y me quedé con las ganas de resolver esta variante :D.

## Entorno de desarrollo
* **Lenguaje:** C
* **Entorno:** Linux
* **Requisitos:** Compilador `gcc` y la librería `pthread`.

Para ejecutar el programa:
1. Abrir la terminal en este directorio.
2. Compilar con: `gcc gatos_ratones.c -o gatos_ratones -lpthread`
3. Ejecutar con: `./gatos_ratones`

## Estrategia de sincronización
Utilicé **Semáforos POSIX** para representar la zona de comida y los platos disponibles, por esta razón es necesario agregar `-lpthread` al compilar. 

El patrón empleado es una adaptación de **Lectores y Escritores** con Exclusión Mutua para el acceso a los recursos compartidos:
* Utilicé un semáforo `zona_comedor` inicializado en 1 para garantizar que si hay gatos en la sala, los ratones no entren (y viceversa).
* Utilicé un semáforo contador `platos_libres` inicializado en 3 ($M$) para limitar la cantidad de animales que pueden comer al mismo tiempo, garantizando que haya un animal por plato.
* Finalmente, utilicé dos semáforos adicionales (`mutex_gatos` y `mutex_ratones`) para proteger los contadores independientes de cada especie y así evitar condiciones de carrera o interbloqueos (deadlocks) al pedir la sala.