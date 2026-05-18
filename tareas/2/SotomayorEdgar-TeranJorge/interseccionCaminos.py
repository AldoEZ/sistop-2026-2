import threading #libreria para hilos
import time #para simular tiempo
import random #para generar autos aleatorios

#semaforos para cada cuadrante (1 auto max por cuadrante)
semaforo_cuadrante_uno = threading.Semaphore(1) #cuadrante 1
semaforo_cuadrante_dos = threading.Semaphore(1) #cuadrante 2
semaforo_cuadrante_tres = threading.Semaphore(1) #cuadrante 3
semaforo_cuadrante_cuatro = threading.Semaphore(1) #cuadrante 4

#torniquete para evitar inanicion
semaforo_torniquete = threading.Semaphore(1) #controla acceso ordenado

#mapa de cuadrantes segun direccion y giro
#orden GLOBAL SIEMPRE creciente para evitar deadlock
def obtener_cuadrantes(direccion_origen, tipo_giro): #devuelve lista de cuadrantes
    if direccion_origen == "N": #desde norte
        if tipo_giro == "derecha": return [semaforo_cuadrante_uno] #solo uno
        if tipo_giro == "recto": return [semaforo_cuadrante_uno,semaforo_cuadrante_dos] #dos
        if tipo_giro == "izquierda": return [semaforo_cuadrante_uno,semaforo_cuadrante_dos,semaforo_cuadrante_tres] #tres
    if direccion_origen == "E": #desde este
        if tipo_giro == "derecha": return [semaforo_cuadrante_dos]
        if tipo_giro == "recto": return [semaforo_cuadrante_dos,semaforo_cuadrante_tres]
        if tipo_giro == "izquierda": return [semaforo_cuadrante_dos,semaforo_cuadrante_tres,semaforo_cuadrante_cuatro]
    if direccion_origen == "S": #desde sur
        if tipo_giro == "derecha": return [semaforo_cuadrante_tres]
        if tipo_giro == "recto": return [semaforo_cuadrante_tres,semaforo_cuadrante_cuatro]
        if tipo_giro == "izquierda": return [semaforo_cuadrante_tres,semaforo_cuadrante_cuatro,semaforo_cuadrante_uno]
    if direccion_origen == "W": #desde oeste
        if tipo_giro == "derecha": return [semaforo_cuadrante_cuatro]
        if tipo_giro == "recto": return [semaforo_cuadrante_cuatro,semaforo_cuadrante_uno]
        if tipo_giro == "izquierda": return [semaforo_cuadrante_cuatro,semaforo_cuadrante_uno,semaforo_cuadrante_dos]

def cruzar_interseccion(identificador_auto, direccion_origen, tipo_giro): #comportamiento del auto
    print(f"Auto {identificador_auto} llega desde {direccion_origen} y gira {tipo_giro}") #log

    semaforo_torniquete.acquire() #entra a cola justa (evita inanicion)

    lista_cuadrantes_necesarios = obtener_cuadrantes(direccion_origen, tipo_giro) #cuadrantes necesarios
    lista_cuadrantes_necesarios = sorted(lista_cuadrantes_necesarios, key=id) #orden global para evitar deadlock

    for semaforo_cuadrante in lista_cuadrantes_necesarios: semaforo_cuadrante.acquire() #toma todos los cuadrantes

    semaforo_torniquete.release() #libera para el siguiente auto

    print(f"Auto {identificador_auto} cruzando...") #en interseccion
    time.sleep(random.uniform(0.5,1.5)) #simula cruce

    for semaforo_cuadrante in lista_cuadrantes_necesarios: semaforo_cuadrante.release() #libera cuadrantes

    print(f"Auto {identificador_auto} salio") #termina

#simulacion
def generar_autos(): #crea autos aleatorios
    lista_direcciones_posibles = ["N","E","S","W"] #posibles direcciones
    lista_tipos_giro = ["derecha","recto","izquierda"] #posibles giros

    for identificador_auto in range(10): #10 autos
        direccion_origen = random.choice(lista_direcciones_posibles) #direccion random
        tipo_giro = random.choice(lista_tipos_giro) #giro random
        threading.Thread(target=cruzar_interseccion, args=(identificador_auto,direccion_origen,tipo_giro)).start() #nuevo hilo
        time.sleep(random.uniform(0.2,0.7)) #llegadas irregulares

generar_autos() #inicia simulacion