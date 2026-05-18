# Tarea 2: Ejercicios de sincronización
**Fecha:** 23 de Marzo 2026   
**Autores:** Blancas Díaz Isaías y Martínez Sánchez Hans  
**Materia:** Sistemas Operativos  
**Grupo:** 07 
 

## 1. Problema Elegido
Se seleccionó el **Ejercicio 7: Santa Claus**. El reto consiste en coordinar a Santa Claus, 9 renos y grupos de 3 elfos utilizando semáforos, asegurando que Santa solo despierte bajo condiciones específicas (cuando lleguen todos los renos o cuando haya un grupo de 3 elfos con dudas).

## 2. Lenguaje y Entorno de Desarrollo
* **Lenguaje:** Python 3.
* **Librerías utilizadas:** * `threading`: Para la gestión de hilos y mecanismos de sincronización (Semáforos).
    * `curses`: Para la creación de la interfaz de usuario en la terminal (TUI).
* **Entorno:** El programa fue desarrollado y probado en un entorno Windows (utilizando `windows-curses`), pero es totalmente compatible con Linux y macOS de forma nativa.

## 3. Instrucciones de Ejecución
Para visualizar la simulación correctamente, se recomiendan los siguientes pasos:

1.  **Maximizar la terminal:** Antes de ejecutar el programa, asegúrese de que la ventana de la terminal esté maximizada para evitar errores en las coordenadas de la interfaz `curses`.
2.  **Instalación de dependencias (Solo en Windows):**
    ```bash
    pip install windows-curses
    ```
3.  **Ejecución:**
    ```bash
    python3 santa_claus.py
    ```
4.  **Finalización:** Para detener la simulación, presione `Ctrl + C`.

## 4. Estrategia de Sincronización
Se emplearon diversos patrones de sincronización utilizando la clase `threading.Semaphore`:

* **Exclusión Mutua (Mutex):** Un semáforo con valor inicial 1 que garantiza que solo un hilo a la vez pueda modificar los contadores globales (`cuenta_renos` y `cuenta_elfos`), evitando condiciones de carrera.
* **Señalización (Signaling):** Santa Claus permanece bloqueado en un `acquire()` sobre el semáforo `santa_sem`. Los hilos de los trabajadores (el noveno reno o el tercer elfo del grupo) ejecutan un `release()` para despertarlo.
* **Barreras de Sincronización:** Se utilizaron semáforos auxiliares (`reno_sem` y `elfo_sem`) para retener a los hilos en un estado de espera hasta que Santa Claus los libera formalmente tras completar su tarea.

## 5. Refinamientos Implementados
Se implementó una **jerarquía de prioridad**. En el bucle principal de Santa Claus, se evalúa primero la condición de los renos. Esto garantiza que, si ambos eventos ocurren simultáneamente, Santa dará prioridad absoluta a la entrega de regalos sobre la atención a los elfos.

## 6. Observaciones y Notas Adicionales
* **Manejo de la Interfaz:** Por las limitaciones de la librería `curses`, el redimensionamiento de la ventana durante la ejecución puede distorsionar el texto. Se recomienda mantener el tamaño de la ventana fijo.
* **Limpieza de Pantalla:** Se implementó un sistema de *padding* (espacios en blanco) al final de cada cadena de texto para que los estados anteriores se borren correctamente y no queden caracteres superpuestos en la terminal.