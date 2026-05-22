import threading
import time
import random

NUM_SILLAS = 3
sillas_disponibles = NUM_SILLAS

# Semaforos
mutex = threading.Semaphore(1)          # Protege la variable sillas_disponibles
alumnos_esperando = threading.Semaphore(0)
asesor_disponible = threading.Semaphore(0)

# Funcion auxiliar para mantener el formato de la tabla
def imprimir_fila(evento, estado_asesor, sillas):
    print(f"{str(evento):<25} | {str(estado_asesor):<20} | {str(sillas):^15}")

def asesor():
    global sillas_disponibles
    while True:
        # El asesor esta libre, pero esperando a que el semaforo se active
        alumnos_esperando.acquire()  

        mutex.acquire()
        sillas_disponibles += 1  # Un alumno deja la silla para entrar a la oficina
        imprimir_fila("Atendiendo alumno", "OCUPADO", sillas_disponibles)
        asesor_disponible.release()
        mutex.release()

        # Simula tiempo de asesoria
        time.sleep(random.randint(1, 3))
        
        mutex.acquire()
        imprimir_fila("Terminó asesoría", "DURMIENDO...", sillas_disponibles)
        mutex.release()

def alumno(id):
    global sillas_disponibles
    while True:
        time.sleep(random.randint(1, 10))  # Llegan en tiempos aleatorios

        mutex.acquire()
        if sillas_disponibles > 0:
            sillas_disponibles -= 1
            imprimir_fila(f"Alumno {id} se sienta", "---", sillas_disponibles)

            alumnos_esperando.release()
            mutex.release()

            asesor_disponible.acquire()
            # El alumno esta recibiendo la clase/asesoria
        else:
            imprimir_fila(f"Alumno {id} se va (lleno)", "---", sillas_disponibles)
            mutex.release()

# --- Configuracion inicial de la tabla ---
print("\n" + "="*65)
print(f"{'ALUMNO / EVENTO':<25} | {'ESTADO ASESOR':<20} | {'SILLAS LIBRES':^15}")
print("="*65)

# Crear hilos
threading.Thread(target=asesor, daemon=True).start()

for i in range(5):
    threading.Thread(target=alumno, args=(i,), daemon=True).start()

# Mantener vivo el programa principal
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nSimulación finalizada.")