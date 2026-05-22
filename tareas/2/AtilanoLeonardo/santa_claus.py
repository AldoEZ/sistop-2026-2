import threading
import time
import random
import curses

TRICICLO_RENOS = 9  # Tienen que ser 9 para que Santa despierte
GRUPO_ELFOS = 3  # Santa solo ayuda de 3 en 3

# Semáforos para que nadie se atropelle
sem_santa = threading.Semaphore(0)
sem_renos = threading.Semaphore(0)
sem_elfos = threading.Semaphore(0)
candado_contador = threading.Lock()  # Nuestro Mutex, si no le pongo el candado aquí
# a veces los contadores se vuelven locos

contador_renos = 0
contador_elfos = 0


def santa_thread(pantalla):
    global contador_renos, contador_elfos
    while True:
        pantalla.addstr(2, 2, "🎅 Santa: Durmiendo... (Esperando llamada)                       ")
        pantalla.refresh()

        sem_santa.acquire()  # Aquí se queda bloqueado hasta que lo despierten

        # Bloqueamos el contador para revisar quién llamó
        candado_contador.acquire()

        # PRIORIDAD: Los renos son primero (Refinamiento para el 10)
        if contador_renos == TRICICLO_RENOS:
            pantalla.addstr(2, 2, "🎅 Santa: ¡Llegaron los renos! ¡A repartir! 🦌💨")
            pantalla.refresh()
            time.sleep(2)  # Simulamos que prepara el trineo
            contador_renos = 0
            for _ in range(TRICICLO_RENOS):
                sem_renos.release()  # Liberamos a los 9 hilos de renos

        elif contador_elfos >= GRUPO_ELFOS:
            pantalla.addstr(2, 2, "🎅 Santa: Ayudando a los elfos con sus juguetes 🛠️ ")
            pantalla.refresh()
            time.sleep(1.5)
            contador_elfos -= GRUPO_ELFOS
            for _ in range(GRUPO_ELFOS):
                sem_elfos.release()  # Liberamos a 3 elfos

        candado_contador.release()


def hilo_reno(id_reno, pantalla):
    global contador_renos
    while True:
        # Los renos andan de vacaciones un rato largo
        time.sleep(random.uniform(8,15))

        candado_contador.acquire()
        contador_renos += 1
        pantalla.addstr(5, 5 + (id_reno * 4), f"R{id_reno}")  # Dibujamos el reno
        if contador_renos == TRICICLO_RENOS:
            sem_santa.release()  # El último reno despierta al jefe
        candado_contador.release()

        sem_renos.acquire()  # Esperan a que Santa los enganche
        pantalla.addstr(5, 5 + (id_reno * 4), "   ")  # Se van al cielo


def hilo_elfo(id_elfo, pantalla):
    global contador_elfos
    while True:
        time.sleep(random.uniform(2, 7))  # Fabricando cosas

        candado_contador.acquire()
        # Solo entran al taller si hay lugar
        if contador_elfos < 3:
            contador_elfos += 1
            pantalla.addstr(8, 5 + (id_elfo * 3), "E")
            if contador_elfos == GRUPO_ELFOS:
                sem_santa.release()

            candado_contador.release()
            sem_elfos.acquire()  # Esperan la ayuda de Santa
            pantalla.addstr(8,5 + (id_elfo * 3), " ")  # Regresan a trabajar
        else:
            # Si ya hay 3, este elfo se espera afuera
            candado_contador.release()


def arranque(stdscr):
    curses.curs_set(0)  # Quitamos el cursor para que se vea limpio
    stdscr.addstr(0, 5, "--- POLO NORTE: TAREA 2 (SINCRO) ---", curses.A_BOLD)

    # Lanzamos a Santa
    threading.Thread(target=santa_thread, args=(stdscr,), daemon=True).start()

    # Lanzamos a los Renos
    for i in range(TRICICLO_RENOS):
        threading.Thread(target=hilo_reno, args=(i, stdscr), daemon=True).start()

    # Lanzamos a unos cuantos Elfos
    for i in range(12):
        threading.Thread(target=hilo_elfo, args=(i, stdscr), daemon=True).start()

    while True: time.sleep(1)


if __name__ == "__main__":
    curses.wrapper(arranque)