# ----------------------
# Santa Claus
# Gonzalez Falcon Luis & Lopez Morales Fernando

import threading
import time
import random
import curses

NUM_ELFOS = 5
NUM_RENOS = 9
NUM_BARRERA_ELFOS = 3 #Se ocupa para definir la barrera para los elfos

MIN_WIDTH = 270

RUTA_SANTA_ZZZ= "zzz.txt" 
RUTA_SANTA_UP = "up.txt"


ASCII_ELFO = [
"   ^ ^   ",
"  (o.o)  ",
"  o(_ )o "
]

ASCII_RENO = [
" ⢀⠴⠀⠀⠀",
" ⠸⢄⡠⢦⠀",
" ⠀⠈⣿⠃⠀",
" ⢳⡿⠿⢿⢤⠀",
" ⠜⠀⠀⠀⠈⠀"
]

# tenemos que crear n elfos y 9 renos
#cada elfo tiene un hilo y cada reno tiene un hilo
#usamos una barrera para los elfos y una barrera para los renos

#Contadores para abrir cada barrera
cuentaBarreraElfos = 0
cuentaBarreraRenos = 0

#Mutex de cada barrera
mutexElfo = threading.Semaphore(1)
mutexReno = threading.Semaphore(1)
mutexSanta = threading.Semaphore(1)

#Barrera de elfos y renos
barreraElfos = threading.Semaphore(0)
barreraRenos = threading.Semaphore(0)  

santaSemaforo = threading.Semaphore(0)

mensaje_santa = ["" for i in range (9)]
mensaje_elfos = ["" for i in range (NUM_ELFOS+1)]
mensaje_elfos_listos = ["" for i in range (4)]
mensaje_renos = ["" for i in range (NUM_RENOS+1)]


def esperar_tamano(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(False) 

    while True:
        stdscr.clear()

        height, width = stdscr.getmaxyx()

        if width >= MIN_WIDTH:
            stdscr.addstr(0, 0, f"Tamaño suficiente detectado ({width} columnas). Presiona cualquier tecla para continuar...")
            stdscr.refresh()
            stdscr.getch()
            break
        else:
            mensaje = "Por favor agranda la terminal a al menos 150 columnas"
            estado = f"Tamaño actual: {width} columnas"

            #Centrar mensaje
            y = height // 2
            x = (width - len(mensaje)) // 2

            stdscr.addstr(y, max(0, x), mensaje)
            stdscr.addstr(y + 1, max(0, (width - len(estado)) // 2), estado)
            stdscr.addstr(y + 3, max(0, (width - 30) // 2), "Esperando redimensionamiento...")

            stdscr.refresh()

            key = stdscr.getch()

            if key == curses.KEY_RESIZE:
                continue  #vuelve a checar tamaoñ

def cargar_ascii(ruta):
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return [line.rstrip("\n") for line in f]
    except:
        return ["Error cargando ASCII"]

def dibujar_caja(stdscr, y, x, h, w):
    for i in range(w):
        stdscr.addch(y, x+i, '-')
        stdscr.addch(y+h, x+i, '-')
    for i in range(h):
        stdscr.addch(y+i, x, '|')
        stdscr.addch(y+i, x+w, '|')


def dibujar_ascii(stdscr, art, y, x):
    for i, line in enumerate(art):
        stdscr.addstr(y+i, x, line)


def dibujar_multiples(stdscr, art, cantidad, y, x, espacio=1):
    for i in range(cantidad):
        dibujar_ascii(stdscr, art, y + i*(len(art)+espacio), x)


def interfaz(stdscr):
    curses.curs_set(0)
    global ascii_santa_zzz
    global ascii_santa_despierto
    global ascii_santa
    ascii_santa_zzz = cargar_ascii(RUTA_SANTA_ZZZ)
    ascii_santa_despierto = cargar_ascii(RUTA_SANTA_UP)
    ascii_santa = ascii_santa_zzz
    esperar_tamano(stdscr)
    while True:
        stdscr.clear()

        h, w = stdscr.getmaxyx()

        third = w // 3
        mitad = (h*5) // 6

        #CAJAS SUPERIORES
        dibujar_caja(stdscr, 0, 0, mitad-1, third-1)
        dibujar_caja(stdscr, 0, third, mitad-1, third-1)
        dibujar_caja(stdscr, 0, 2*third, mitad-1, third-1)

        # CAJAS INFERIORES
        altura_inferior = h - mitad - 1

        dibujar_caja(stdscr, mitad, 0, altura_inferior, third-1)
        dibujar_caja(stdscr, mitad, third, altura_inferior, third-1)
        dibujar_caja(stdscr, mitad, 2*third, altura_inferior, third-1)

        # SANTA (IZQUIERDA)
        dibujar_ascii(stdscr, ascii_santa, 2, 2) 

        for i in range (9):
            stdscr.addstr(mitad+1+i, 2, mensaje_santa[i])

        # ELFOS (CENTRO)
        dibujar_multiples(stdscr, ASCII_ELFO, cuentaBarreraElfos, 2, third+2)

        for i in range (NUM_ELFOS):
            stdscr.addstr(mitad+1+(i), third+2, mensaje_elfos[i]) 
        for i in range (4):
            stdscr.addstr(mitad+1+6+i, third+2, mensaje_elfos_listos[i]) 

        # RENOS (DERECHA)
        dibujar_multiples(stdscr, ASCII_RENO, cuentaBarreraRenos, 2, 2*third+2)

        for i in range (NUM_RENOS):
            stdscr.addstr(mitad+1+i, 2*third+2, mensaje_renos[i]) 

        stdscr.refresh()

        time.sleep(0.2)
"""
        key = stdscr.getch()
        
        if key == ord('q'):
            break
"""


def accionReno(num):
    while True:
        mensaje_renos[num] = f"Soy el reno {num} y estoy vacacionando :D"
        numRandom = random.randint(1,1000)
        while(numRandom != 10):
            numRandom = random.randint(1,1000)
            time.sleep(0.01)
        mensaje_renos[num] = f"RENO {num} esta de vuelta"
        llamadaRenos(num)

def llamadaRenos(num):
    global cuentaBarreraRenos
    mutexReno.acquire()
    cuentaBarreraRenos = cuentaBarreraRenos+1
    if cuentaBarreraRenos == 9:
        mensaje_renos[9] = "YA LLEGAMOS LOS 9 RENOS"
        santaSemaforo.release()
    mutexReno.release()
    barreraRenos.acquire()



def trabajoElfo(num):
    while True:
        # print(f"Soy el elfo {num} y estoy trabajando...")
        mensaje_elfos[num] = f"Soy el elfo {num} y estoy trabajando..."

        numRandom = random.randint(1,100)
        while(numRandom != 10):
            time.sleep(0.7)
            numRandom = random.randint(1,10)
        # print(f"Elfo {num} encontre un problema")
        mensaje_elfos[num] = f"Elfo {num} encontre un problema"
        llamadaProblema(num)


#Funcion donde se gestiona la barrera de elfo
def llamadaProblema(num):
    global cuentaBarreraElfos
    mutexElfo.acquire()
    if cuentaBarreraElfos < NUM_BARRERA_ELFOS:
        cuentaBarreraElfos += 1
        # print(f"[{num}] me formo para pedir ayuda a santa: {cuentaBarreraElfos} esperando")
        mensaje_elfos_listos[cuentaBarreraElfos] = f"[{num}] me formo para pedir ayuda a santa: {cuentaBarreraElfos} esperando"
        if cuentaBarreraElfos == NUM_BARRERA_ELFOS:
             # print("Hablando a Santa porque somos 3")
            santaSemaforo.release()
        mutexElfo.release()
        barreraElfos.acquire()
        # print("Los elfos se ponen a trabajar de nuevo")
        mensaje_elfos_listos[3] = "Los elfos se ponen a trabajar de nuevo"
    else: # Cuando hay 3 elfos, se ponen a trabajar de nuevo
        # print("Ya hay 3 elfos actualmente, regresare a trabajar")
        mensaje_santa[3] = "Los elfos se ponen a trabajar de nuevo"
        mutexElfo.release()
        #time.sleep(5)


def santaAyudando():
    global cuentaBarreraElfos, cuentaBarreraRenos, ascii_santa
    while True:
        santaSemaforo.acquire() # Se duemre hasta que los renos o los elfos lo despierten
        #Revisando si son los renos o los elfos
        mutexReno.acquire()
        ascii_santa = ascii_santa_despierto
        if cuentaBarreraRenos == 9:
            
            for i in range(9):
                mensaje_santa[i] = ""
            mensaje_santa[0] = "ES NAVIDAD A ENTREGAR LOS REGALOS!!!"
            
            # SE TIENE QUE DESPERTAR!!

            #liberando a los 9 renos (optimizar con for)
            barreraRenos.release()
            barreraRenos.release()
            barreraRenos.release()
            barreraRenos.release()
            barreraRenos.release()
            barreraRenos.release()
            barreraRenos.release()
            barreraRenos.release()
            barreraRenos.release()
            cuentaBarreraRenos = 0
            
            mensaje_santa[1] = "¡¡¡REGALOS ENTREGADOS, VUELVO A DORMIR!!!"
            time.sleep(2)
            for i in range(9):
                mensaje_santa[i] = ""
        ascii_santa = ascii_santa_zzz
        mutexReno.release()


        mutexElfo.acquire()
        if cuentaBarreraElfos == NUM_BARRERA_ELFOS:
            
            mensaje_santa[3] = "<<<DESPERTE Y VOY A AYUDAR>>>"
            ascii_santa = ascii_santa_despierto
            
            barreraElfos.release()
            barreraElfos.release()
            barreraElfos.release()
            time.sleep(2)

            #Se resetea
            cuentaBarreraElfos = 0
            for i in range (4):
                mensaje_elfos_listos[i] = ""
            
            mensaje_santa[3] = "<<<VOLVERE A DORMIR>>>"
            ascii_santa = ascii_santa_zzz
        mutexElfo.release()

#Creando hilo Santa Claus
threading.Thread(target=santaAyudando, args=()).start() 

#creando hilos ELFOS
for i in range(NUM_ELFOS):
    threading.Thread(target= trabajoElfo, args=[i]).start()

#Creando hilos renos
for i in range(NUM_RENOS):
    threading.Thread(target= accionReno, args=[i]).start()


curses.wrapper(interfaz)