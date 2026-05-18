import threading
import time
import random
import curses

#definimos el numero de personajes planteados
total_renos = 9
grupo_elfos = 3
total_elfos_taller = 10

#definimos las herramientas de sincronizacion (semaforos):

#mutex para que solo un hilo a la vez mueva los contadores
mutex = threading.Semaphore(1)

#santa_sem:donde santa se queda dormido 
santa_sem = threading.Semaphore(0)

#reno_sem: para detener a los renos hasta que empiece su recorrido
reno_sem = threading.Semaphore(0)

#elfo_sem: para que los elfos esperen frente a la oficina de santa
elfo_sem = threading.Semaphore(0)

#contadores: para saber cuantos elfos y renos han llegado
cuenta_renos = 0
cuenta_elfos = 0

def santa():
    global cuenta_renos, cuenta_elfos
    while True:
        #santa anda durmiendo
        #agregamos espacios extras al final para limpiar mensajes largos anteriores
        actualizar_estado(10, 2, "santa esta durmiendo zzzzz                     ")
        santa_sem.acquire() 
        
        #santa se desperto por una causa
        mutex.acquire()
        
        #causa 1: llegaron todos los renos
        if cuenta_renos == total_renos:
            actualizar_estado(10, 2, "amonos a repartir regalos!                     ")
            #enganchamos a los 9 renos
            for _ in range(total_renos):
                reno_sem.release()
            cuenta_renos = 0
            time.sleep(3) #simulamos que santa reparte los regalos
            
        #causa 2: hay 3 elfos con dudas
        elif cuenta_elfos == grupo_elfos:
            actualizar_estado(10, 2, "santa esta ayudando a sus 3 elfos              ")
            #liberamos a los 3 elfos que estaban esperando
            for _ in range(grupo_elfos):
                elfo_sem.release()
            cuenta_elfos = 0
            time.sleep(2) #simulamos que santa explica las dudas
            
        mutex.release()

def reno(id_reno):
    global cuenta_renos
    #los renos viven en un bucle infinito
    while True:
        #simula que estan de vacaciones (entre 10 y 15 seg.)
        time.sleep(random.uniform(10, 15))
        
        mutex.acquire()
        cuenta_renos += 1
        #el espacio extra al final borra estados anteriores mas largos
        actualizar_estado(2, id_reno * 12, f"r{id_reno}:llegó   ")
        
        #si el reno 9 llega, santa se despierta
        if cuenta_renos == total_renos:
            santa_sem.release()
        mutex.release()
        
        #el reno se queda parado aqui hasta que santa haga reno_sem.release()
        reno_sem.acquire()
        actualizar_estado(2, id_reno * 12, f"r{id_reno}:vuela   ")
        time.sleep(3)

def elfo(id_elfo):
    global cuenta_elfos
    while True:
        #el elfo trabaja un rato antes de tener una duda
        time.sleep(random.uniform(6, 10))
        
        mutex.acquire()
        #solo si hay menos de 3 esperando, este elfo puede ir a pedir ayuda
        if cuenta_elfos < grupo_elfos:
            cuenta_elfos += 1
            actualizar_estado(6, id_elfo * 10, f"e{id_elfo}:duda   ")
            
            #si este elfo es el tercero del grupo, despierta a santa
            if cuenta_elfos == grupo_elfos:
                santa_sem.release()
            mutex.release()
            
            #el elfo se queda esperando en la puerta
            elfo_sem.acquire()
            actualizar_estado(6, id_elfo * 10, f"e{id_elfo}:espera  ")
            time.sleep(2)
        else:
            #si ya hay 3 elfos esperando, este elfo sigue debe seguir trabajando
            mutex.release()
            actualizar_estado(6, id_elfo * 10, f"e{id_elfo}:trabaja  ")

#funciones de apoyo para la pantalla (curses)
def actualizar_estado(y, x, texto):
    try:
        #escribe en la terminal en una posicion especifica
        stdscr.addstr(y, x, str(texto))
        stdscr.refresh()
    except:
        pass

def principal(window):
    global stdscr
    stdscr = window
    stdscr.clear()
    #ocultamos el cursor para que se vea mas limpio
    try:
        curses.curs_set(0)
    except:
        pass

    #etiquetas fijas para dar orden visual
    actualizar_estado(1, 2, "estado de los renos:")
    actualizar_estado(5, 2, "estado de los elfos:")
    actualizar_estado(9, 2, "estado de santa:")
    
    #creamos y lanzamos el hilo de santa
    hilo_santa = threading.Thread(target=santa, daemon=True)
    hilo_santa.start()
    
    #creamos los hilos de los renos
    for i in range(total_renos):
        threading.Thread(target=reno, args=(i,), daemon=True).start()
        
    #creamos los hilos de los elfos
    for i in range(total_elfos_taller):
        threading.Thread(target=elfo, args=(i,), daemon=True).start()
        
    #el programa principal se queda aqui para que no se cierre
    while True:
        time.sleep(1)

if __name__ == "__main__":
    #inicializa el entorno de curses
    curses.wrapper(principal)