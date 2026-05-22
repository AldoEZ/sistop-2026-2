#!/usr/bin/python3
import threading
import time
import random
from queue import Queue

NUM_SILLAS = 3       # Capacidad de la sala de espera
NUM_ALUMNOS = 6      # Número de hilos alumno

# Cola FIFO para mantener orden de llegada
cola = Queue()

# Semáforos principales
mutex = threading.Semaphore(1)     # Protege acceso a la cola y diccionario
alumnos = threading.Semaphore(0)   # Cuenta alumnos en espera

# Semáforos individuales por alumno
turnos = {}

# Métricas del sistema
atendidos = 0
rechazados = 0
sem_metricas = threading.Semaphore(1)  # Protege métricas


def asesor():
    global atendidos

    while True:
        print("\nProfesor: durmiendo...")
        alumnos.acquire()  # Espera hasta que haya alumnos

        # Obtener siguiente alumno
        mutex.acquire()
        alumno_id, llegada = cola.get()
        espera = time.time() - llegada

        print(f"Profesor: atiende alumno {alumno_id} (en cola: {cola.qsize()})")

        # Despierta únicamente al alumno correspondiente
        sem = turnos.pop(alumno_id)
        sem.release()
        mutex.release()

        # Simulación de preguntas
        preguntas = random.randint(1, 3)
        for i in range(preguntas):
            print(f"Alumno {alumno_id} realiza pregunta {i+1}")
            time.sleep(random.uniform(0.5, 1.5))

        print(f"Profesor: terminó con alumno {alumno_id} (esperó {espera:.2f}s)\n")

        # Actualiza métricas
        sem_metricas.acquire()
        atendidos += 1
        sem_metricas.release()


def alumno(id):
    global rechazados

    while True:
        # Llegadas aleatorias
        time.sleep(random.uniform(1, 4))
        print(f"Alumno {id}: llega")

        mutex.acquire()
        if cola.qsize() < NUM_SILLAS:
            # Crea su propio semáforo de turno
            turnos[id] = threading.Semaphore(0)

            # Se agrega a la cola de espera
            cola.put((id, time.time()))
            print(f"Alumno {id}: se sienta (en cola: {cola.qsize()})")

            alumnos.release()  # Notifica al profesor
            mutex.release()

            # Espera hasta que el profesor lo atienda
            turnos[id].acquire()

            print(f"Alumno {id}: siendo atendido")
            print(f"Alumno {id}: se retira\n")

        else:
            # No hay sillas disponibles
            mutex.release()
            print(f"Alumno {id}: se retira (no hay sillas)\n")

            # Actualiza métricas
            sem_metricas.acquire()
            rechazados += 1
            sem_metricas.release()


def monitor():
    global atendidos, rechazados

    while True:
        time.sleep(10)

        # Muestra estadísticas periódicamente
        sem_metricas.acquire()
        print("\n----- ESTADÍSTICAS -----")
        print(f"Alumnos atendidos: {atendidos}")
        print(f"Alumnos rechazados: {rechazados}")
        print("------------------------\n")
        sem_metricas.release()


threading.Thread(target=asesor, daemon=True).start()
threading.Thread(target=monitor, daemon=True).start()

# Crear hilos de alumnos
for i in range(NUM_ALUMNOS):
    threading.Thread(target=alumno, args=(i,), daemon=True).start()

# Mantener el programa en ejecución
while True:
    time.sleep(1)
