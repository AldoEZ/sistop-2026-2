import threading
import queue
import time
from filesystem import FiUnamFS

fs = FiUnamFS('fiunamfs.img')

if not fs.validar_fs():
    print('Sistema de archivos invalido.')
    exit()

# Mecanismo de comunicación entre hilos: una cola para enviar tareas y una variable de estado para informar al usuario
cola_tareas = queue.Queue()
estado_fs = "LIBRE"  # Variable de estado compartida


def trabajador_fs():
    """
    Este hilo corre en segundo plano. Espera tareas en la cola, 
    actualiza el estado del FS y ejecuta las operaciones concurrentemente.
    """
    global estado_fs
    while True:
        tarea = cola_tareas.get()
        if tarea is None:  # Señal para apagar el hilo
            break

        # Comunica que el sistema está trabajando
        estado_fs = "TRABAJANDO"
        print(
            "\n[Trabajador] Estado: TRABAJANDO. Ejecutando operación en FiUnamFS...")

        funcion, args = tarea
        try:
            funcion(*args)
        except Exception as e:
            print(f"[Trabajador] Error en la operación: {e}")

        # Comunica que el sistema se liberó
        estado_fs = "LIBRE"
        print("[Trabajador] Operación finalizada. Estado: LIBRE.")
        print("-> Presiona ENTER para mostrar el menú de nuevo...")

        cola_tareas.task_done()


# Inicia el hilo trabajador una sola vez al arrancar el programa
hilo_worker = threading.Thread(target=trabajador_fs)
hilo_worker.start()

# Hilo principal: muestra el menú y envía tareas al trabajador sin bloquearse
while True:
    # Muestra el estado actual en el menú (comunicación de estado)
    print(f'\n===== FiUnamFS (Estado: {estado_fs}) =====')
    print('1. Listar archivos')
    print('2. Copiar desde FiUnamFS')
    print('3. Copiar hacia FiUnamFS')
    print('4. Eliminar archivo')
    print('5. Salir')

    opcion = input('Selecciona una opcion: ')

    if opcion == '1':
        # En vez de ejecutar y bloquear, manda la función a la cola
        cola_tareas.put((fs.mostrar_archivos, ()))
        # Breve pausa para que la terminal no se sature de mensajes si el usuario selecciona opciones rápidamente
        time.sleep(0.1)

    elif opcion == '2':
        nombre = input('Archivo a copiar: ')
        destino = input('Ruta destino: ')
        cola_tareas.put((fs.copiar_desde_fs, (nombre, destino)))
        time.sleep(0.1)

    elif opcion == '3':
        ruta = input('Ruta del archivo local: ')
        cola_tareas.put((fs.copiar_hacia_fs, (ruta,)))
        time.sleep(0.1)

    elif opcion == '4':
        nombre = input('Archivo a eliminar: ')
        cola_tareas.put((fs.eliminar_archivo, (nombre,)))
        time.sleep(0.1)

    elif opcion == '5':
        print("Cerrando sistema y esperando a que terminen las operaciones pendientes...")
        cola_tareas.put(None)  # Manda la señal de apagado al trabajador
        hilo_worker.join()    # Espera a que el trabajador muera para salir del programa
        break

    else:
        print('Opcion invalida.')
