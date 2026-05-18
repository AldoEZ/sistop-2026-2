import random
import curses
from threading import Thread, Semaphore, Lock
import time

#CONSTANTES
NECESITA_AYUDA = 3 #Num elfos necesarios para despertar a Santa
MAX_ELFOS = 10 #Num elfos totales
NUM_RENOS = 9 #Num renos totales

#Variables para el manejo de estados en la interfaz
estado_santa = "Durmiendo ZZZ" 
estado_elfo = ["Trabajando"] * MAX_ELFOS
estado_reno = ["Vacaciones"] * NUM_RENOS

#Contadores
contador_elfos = 0 #Permite contar cuantos elfos necesitan ayuda
contador_renos = 0 #Permite contar cuantos renos vuelven de vacaciones

#Semáforo
santaSem = Semaphore(0) #Sirve para controlar el hilo de santa. 
renoSem = Semaphore(0) #Sirve para controlar el hilo de santa.

#Mutex
mutex_num_elfos = Semaphore(3) #Permite el control de 3 renos 
mutex = Semaphore(1) #Permite el control del acceso a las variables contador
screen_lock = Lock()  # Control de la interfaz

def santa(stdscr):
    global contador_elfos, contador_renos, estado_santa
    
    while True:
        santaSem.acquire()

        with mutex:
            estado_santa = "Despierto ZZZZzzz"
            
            if contador_renos == NUM_RENOS:
                estado_santa = "Repartiendo regalos"
                contador_renos = 0

                time.sleep(2) # Tiempo de entrega

                for _ in range(NUM_RENOS): #Libera a los renos
                    renoSem.release()
                estado_santa = "Durmiendo ZZZ"
                
            if contador_elfos == NECESITA_AYUDA:
                estado_santa = "Ayudando a los elfos"
                contador_elfos = 0

                time.sleep(1.5) # Tiempo de resolución de dudas

                for _ in range(NECESITA_AYUDA): #Permite que se formen 3 nuevos elfos
                    mutex_num_elfos.release()
                estado_santa = "Durmiendo ZZZ"

def renos(n):
    global contador_renos, estado_reno

    while True:
        time.sleep(random.uniform(5, 10)) # Tiempo en vacaciones
        
        with mutex:
            contador_renos += 1
            estado_reno[n] = "En espera"
            if contador_renos == NUM_RENOS:
                santaSem.release()
        
        renoSem.acquire()
        estado_reno[n] = "Vacaciones"

def elfos(n):
    global contador_elfos, estado_elfo
    while True:
        time.sleep(random.uniform(4, 20)) # Tiempo trabajando 
        
        mutex_num_elfos.acquire() 
        with mutex:
            contador_elfos += 1
            estado_elfo[n] = "Necesita ayuda"
            if contador_elfos == NECESITA_AYUDA:
                santaSem.release()
        
        #Control de impresión el la interfaz

        # Simula esperar a que Santa termine 
        while estado_elfo[n] == "Necesita ayuda":
            if contador_elfos == 0: # Santa ya los ayudó
                estado_elfo[n] = "Trabajando"
            time.sleep(0.1)

def draw_ui(stdscr):
    stdscr.nodelay(1)  # No bloquear al esperar input
    
    while True:
        with screen_lock:
            stdscr.erase()
            h, w = stdscr.getmaxyx()

            #Titulo
            stdscr.addstr(1, 2, " PROBLEMA DE SANTA CLAUS ", curses.A_BOLD)
            stdscr.addstr(3, 2, f"Estado de Santa: {estado_santa}")
            
            #RENOS ---
            stdscr.addstr(5, 2, "RENOS:", curses.A_UNDERLINE)
            for i, status in enumerate(estado_reno):
                color = curses.A_DIM if status == "Vacaciones" else curses.A_BOLD
                stdscr.addstr(6 + i, 4, f"Reno {i}: {status}", color)
            stdscr.addstr(6 + NUM_RENOS, 2, f"Total que volvieron: {contador_renos}/{NUM_RENOS}")

            #ELFOS
            stdscr.addstr(5, 40, "ELFOS:", curses.A_UNDERLINE)
            for i, status in enumerate(estado_elfo):
                color = curses.A_BOLD if status == "Necesita ayuda" else curses.A_DIM
                stdscr.addstr(6 + i, 42, f"Elfo {i}: {status}", color)
            stdscr.addstr(6 + MAX_ELFOS, 40, f"Esperando ayuda: {contador_elfos}/{NECESITA_AYUDA}")

            stdscr.addstr(h-2, 2, "Presiona 'q' para salir.")
            stdscr.refresh()

        if stdscr.getch() == ord('q'):
            break
        time.sleep(0.1)

def main(stdscr):
    
    #Inicialización de hilos
    Thread(target=santa, args=(stdscr,), daemon=True).start()
    for i in range(NUM_RENOS):
        Thread(target=renos, args=(i,), daemon=True).start()
    for i in range(MAX_ELFOS):
        Thread(target=elfos, args=(i,), daemon=True).start()
    
    #Inicia impresión de la interfaz
    draw_ui(stdscr)

if __name__ == "__main__":
    curses.wrapper(main)