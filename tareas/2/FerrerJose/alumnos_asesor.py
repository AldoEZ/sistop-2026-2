import threading
import time
import random

NUM_SILLAS = 3
NUM_ALUMNOS = 6
PREGUNTAS_MAXIMAS = 3

sillas_disponibles = NUM_SILLAS
mutex = threading.Lock()
alumnos_esperando = threading.Semaphore(0)
asesor_listo = threading.Semaphore(0)

cola_alumnos = []


def asesor():
    global sillas_disponibles

    while True:
        print("Asesor: no hay alumnos voy a dormir un rato.")
        alumnos_esperando.acquire()

        with mutex:
            if len(cola_alumnos) == 0:
                continue

            alumno_id = cola_alumnos.pop(0)
            sillas_disponibles += 1
            print(f"Asesor: voy a atender al alumno {alumno_id}.")
            print(f"Asesor: sillas disponibles = {sillas_disponibles}")

        asesor_listo.release()

        tiempo_asesoria = random.uniform(1, 2.5)
        time.sleep(tiempo_asesoria)

        print(f"Asesor: terminé de atender al alumno {alumno_id}.")


def alumno(alumno_id):
    global sillas_disponibles

    preguntas = random.randint(1, PREGUNTAS_MAXIMAS)

    for pregunta in range(1, preguntas + 1):
        time.sleep(random.uniform(0.5, 3))

        print(f"Alumno {alumno_id}: llegó con la pregunta {pregunta}.")

        with mutex:
            if sillas_disponibles > 0:
                sillas_disponibles -= 1
                cola_alumnos.append(alumno_id)
                print(f"Alumno {alumno_id}: se sienta a esperar.")
                print(f"Alumno {alumno_id}: sillas disponibles = {sillas_disponibles}")
            else:
                print(f"Alumno {alumno_id}: no hay sillas disponibles, me voy y regreso después.")
                continue

        alumnos_esperando.release()
        asesor_listo.acquire()

        print(f"Alumno {alumno_id}: está siendo atendido.")

        time.sleep(random.uniform(0.5, 1.5))

        print(f"Alumno {alumno_id}: terminó su pregunta {pregunta}.")

    print(f"Alumno {alumno_id}: ya no tiene más preguntas.")


def main():
    hilo_asesor = threading.Thread(target=asesor, daemon=True)
    hilo_asesor.start()

    hilos_alumnos = []
    for i in range(1, NUM_ALUMNOS + 1):
        t = threading.Thread(target=alumno, args=(i,))
        hilos_alumnos.append(t)
        t.start()

    for t in hilos_alumnos:
        t.join()

    print("Todos los alumnos terminaron. Gracias por esperar")


if __name__ == "__main__":
    main() 