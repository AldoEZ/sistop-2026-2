
#TAREA 02
#FECHA DE ENTREGA: 26 DE MARZO 2026
#AUTORES: Bello Sánchez Santiago Arath y López Romero David Baruc

import threading
import time
import random
# El programa fue probado con 10 usuarios inicialmente, sin embargo se ejemplifica mucho mejor con 20 y hasta el momento funciona :) . 
NUM_USR = 20 #Todo correcto si desea modificar el valor de los usuarios.
PISOS = 5 
PISO_ACT = 0
DIR = 0
USR_ESPERANDO = [0,0,0,0,0,0] 
LIMITE = 5

semaforo_lugares = threading.Semaphore(LIMITE)
semaforo_solicitud = threading.Semaphore(1)

pasajeros_actuales = 0
mutex_pasajeros = threading.Lock()
mensajes_usuarios = []
mutex_mensajes = threading.Lock()

def facultad():
    
    threading.Thread(target=elv, daemon=True).start()
    threading.Thread(target=estado, daemon=True).start() 

    for i in range(NUM_USR):
     
        x = random.randint(0, PISOS) 

        y = random.randint(0, PISOS) 


        while (y == x):
            y = random.randint(0, PISOS)

        threading.Thread(target=user, args=(i, x, y)).start()
        time.sleep(0.5) 

    time.sleep(20) 
    print("\n--- fin... ---")

def estado():

    global PISO_ACT, USR_ESPERANDO, pasajeros_actuales

    piso_anterior = -1
    
    while True:
        if PISO_ACT != piso_anterior:
            piso_anterior = PISO_ACT
            
            print("\n" + "="*35)
            print(" ESTADO DEL EDIFICIO ".center(35, "="))

            aux = 0
            for i in range(PISOS, -1, -1):

                esperando = "i" * USR_ESPERANDO[i]
                
       
                if i == PISO_ACT:

                    with mutex_pasajeros:

                        dentro = "i" * pasajeros_actuales

                    elevador_dibujo = f"[{dentro:<5}] 🛗" 
                else:
                    elevador_dibujo = "[     ]"
                
            
                print(f"Piso {i} | Esperan: {esperando:<10} | {elevador_dibujo}")
                
            print("="*35 + "\n")
      
  
        time.sleep(0.1)


def user(numero_user, x, y):

    global PISO_ACT, USR_ESPERANDO, pasajeros_actuales

    semaforo_solicitud.acquire()

    USR_ESPERANDO[x] += 1

    semaforo_solicitud.release()

    while True: 

        if x == PISO_ACT:

            if semaforo_lugares.acquire(blocking=False):
  
                with mutex_pasajeros:

                    pasajeros_actuales += 1

                with mutex_mensajes:
                    mensaje_subida = f"Usuario {numero_user}: Estoy en piso {x} y voy a piso {y}"
                    mensajes_usuarios.append(mensaje_subida)
                    print(mensaje_subida)

                break 
        time.sleep(0.1)

    semaforo_solicitud.acquire()

    USR_ESPERANDO[x] -= 1

    semaforo_solicitud.release()


    while True:
        if y == PISO_ACT:
     
            with mutex_pasajeros:

                pasajeros_actuales -= 1

            with mutex_mensajes:
                mensaje_bajada = f"Usuario {numero_user}: Me bajo en {y}"
                mensajes_usuarios.append(mensaje_bajada)
                print(mensaje_bajada)

            semaforo_lugares.release()
            break
        time.sleep(0.1)

def elv():
    global PISO_ACT, DIR

    while True:

        if PISO_ACT == 0:

            DIR = 1

        elif PISO_ACT == PISOS:

            DIR = -1
            
        PISO_ACT += DIR 
        
   
        if USR_ESPERANDO[PISO_ACT] > 0:

            time.sleep(0.5)

 
        time.sleep(0.8)

facultad()