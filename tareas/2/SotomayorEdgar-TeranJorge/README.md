SIMULACIÓN DE INTERSECCIÓN SIN SEÑALAMIENTO USANDO SEMÁFOROS --> "interseccionCaminos.py"

DESCRIPCIÓN DEL PROBLEMA

Se modela una intersección de cuatro direcciones sin señalamiento vial, donde los autos pueden llegar desde cualquier dirección y en cualquier momento. El objetivo es garantizar:

* Que no ocurran choques (exclusión mutua por sección de la intersección)
* Que no exista inanición
* Que el sistema sea eficiente (permitir concurrencia cuando sea posible)
* Que no se presenten bloqueos mutuos

LENGUAJE Y ENTORNO DE DESARROLLO

El programa fue desarrollado en Python utilizando la librería estándar "threading", la cual permite la creación de hilos y el uso de semáforos para sincronización.

REQUISITOS PARA EJECUTAR EL PROGRAMA

No se requieren dependencias externas ni configuración adicional.

IDEA GENERAL DE LA SOLUCIÓN

La intersección se divide en 4 cuadrantes independientes. Cada auto necesita ocupar uno o más cuadrantes dependiendo de su trayectoria:

* Giro a la derecha --> 1 cuadrante
* Movimiento recto --> 2 cuadrantes
* Giro a la izquierda --> 3 cuadrantes

Cada cuadrante está protegido por un semáforo binario.

MECANISMOS DE SINCRONIZACIÓN UTILIZADOS

1. Exclusión mutua por cuadrante

Cada cuadrante tiene su propio semáforo:

* semaforo_cuadrante_uno
* semaforo_cuadrante_dos
* semaforo_cuadrante_tres
* semaforo_cuadrante_cuatro

Esto garantiza que no haya dos autos en la misma sección al mismo tiempo, evitando choques.

2. Evitar bloqueo total de la intersección

No se usa un único semáforo global. En su lugar:

* Cada auto adquiere solo los cuadrantes que necesita
* Esto permite que varios autos crucen simultáneamente si sus trayectorias no se intersectan

Ejemplo: cuatro autos girando a la derecha pueden cruzar al mismo tiempo.

3. Evitar interbloqueos

Se impone un orden global de adquisición de recursos:

lista_cuadrantes_necesarios = sorted(lista_cuadrantes_necesarios, key=id)

Todos los autos adquieren los semáforos en el mismo orden, eliminando ciclos de espera y evitando deadlocks.

4. Evitar inanición

Se usa un semáforo adicional tipo torniquete:

* semaforo_torniquete

Antes de adquirir los cuadrantes, cada auto pasa por este semáforo:

semaforo_torniquete.acquire()

Esto fuerza un acceso ordenado, asegurando que ningún auto espere indefinidamente.

5. Liberación controlada

Después de adquirir todos los cuadrantes:

* Se libera el torniquete para permitir que otro auto avance
* El auto cruza la intersección
* Finalmente libera los cuadrantes

ESTRATEGIA DE SINCRONIZACIÓN EMPLEADA

La solución utiliza una combinación de mecanismos de sincronización:

* Semáforos binarios (mutex implícitos) para controlar el acceso a cada cuadrante
* Orden global de adquisición de recursos para prevenir interbloqueos
* Torniquete (turnstile) para garantizar equidad y evitar inanición

Este enfoque corresponde a un patrón clásico de control de concurrencia basado en recursos compartidos con prevención de deadlocks y fairness.

MODELADO DE GIROS

La función obtener_cuadrantes(direccion_origen, tipo_giro) determina qué recursos necesita cada auto:

* Dirección: N, E, S, W
* Giro: derecha, recto, izquierda

Esto permite una simulación más realista y eficiente.

FLUJO DE EJECUCIÓN DE UN AUTO

1. Llega a la intersección
2. Pasa por el torniquete (control de fairness)
3. Calcula los cuadrantes necesarios
4. Los ordena globalmente
5. Adquiere todos los semáforos requeridos
6. Libera el torniquete
7. Cruza la intersección
8. Libera los cuadrantes

VENTAJAS DE LA SOLUCIÓN

* Evita choques mediante exclusión por cuadrante
* Permite concurrencia real
* Previene deadlocks con orden global
* Reduce inanición con torniquete

IMPLEMENTACIÓN DE REFINAMIENTOS

Sí se están implementando los refinamientos planteados:

* No se bloquea toda la intersección: solo se ocupan los cuadrantes necesarios
* Se mejora el rendimiento permitiendo concurrencia parcial
* Se reduce la inanición mediante el uso del torniquete
* Se modelan correctamente los giros (derecha, recto, izquierda)
* Se evita el bloqueo mutuo mediante orden global de adquisición de recursos