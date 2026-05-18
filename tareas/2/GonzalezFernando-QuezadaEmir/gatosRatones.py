from threading import Semaphore, Thread
import time
import random

NUMERO_GATOS_PROBLEMA = 6
NUMERO_RATONES_PROBLEMA = 10
NUMERO_PLATOS = 5

ratonesComiendo = 0
gatosComiendo = 0
ratonesRIP = 0

platos = Semaphore(NUMERO_PLATOS)
mutexRaton = Semaphore(1)           #Protege variables de ratón
mutexGato = Semaphore(1)            #Protege variables de gato
ratonEnCuarto = Semaphore(1)        #Evita que entren gatos si hay ratones
torniquete = Semaphore(1)           #Necesario para evitar la inanición


def raton(id):
    global ratonesComiendo
    global gatosComiendo
    global ratonesRIP
    tiempo =[0.5, 0.6, 0.7, 0.8, 0.9, 1]

    #Torquiquete, necesario para que no ganen eternamente los ratones
    torniquete.acquire()
    torniquete.release()

    #Permitimos que nuestro hermoso ratón llegue al plato
    platos.acquire()
    
    #Empieza la tensión
    mutexRaton.acquire()

    #Si había un gato en la habitación, nos despedimos de nuestra ratita
    if(gatosComiendo>0):
        print(f"[raton {id}]: Intentó comer pero es descubierto y sufre las consecuencias de su avaricia")
        platos.release()
        ratonesRIP+=1
        mutexRaton.release()
        return
    
    #Contabilizamos al ratón 
    ratonesComiendo += 1
    if ratonesComiendo == 1:
        ratonEnCuarto.acquire()   #Bloqueamos la entrada de gatos
    print(f"[raton {id}]: Comiendo")
    
    mutexRaton.release()

    #Simulamos el tiempo que tarda en comer
    time.sleep(random.choice(tiempo))  
    #El ratón libera el plato y se retira triunfantemente
    mutexRaton.acquire()

    ratonesComiendo -= 1
    if ratonesComiendo == 0:
        ratonEnCuarto.release()   #Permitimos la entrada de gatos
    
    mutexRaton.release()
    platos.release()

    print(f"[raton {id}]: Comió exitosamente y vivió para contarlo")  


def gato(id):
    global gatosComiendo
    

    #Dado que el ratón tiempre tendrá prioridad, pedimos prestado más tiempo para un gato
    torniquete.acquire()
    mutexGato.acquire() #El gato intenta entrar...

    gatosComiendo += 1
    if gatosComiendo==1:
        #El primer gato espera a que los ratones se vayan
        ratonEnCuarto.acquire()

    mutexGato.release()
    torniquete.release()

    #Tomamos un plato y comemos tranquilamente
    platos.acquire()
    print(f"[gato {id}]: Comiendo")
    
    #Liberamos el plato y nos retiramos
    mutexGato.acquire()
    
    gatosComiendo -= 1
    if gatosComiendo==0:
        ratonEnCuarto.release()
    
    mutexGato.release()
    platos.release()

    print(f"[gato {id}:] Termina de comer y se va a jugar")


#Creamos nuestros hilos
hilos = []

for j in range(NUMERO_RATONES_PROBLEMA):
    t = Thread(target=raton, args=[j])
    hilos.append(t)

for i in range(NUMERO_GATOS_PROBLEMA):
    t = Thread(target=gato, args=[i])
    hilos.append(t)

#Creamos "aleatoriedad" para el comienzo de los hilos
random.shuffle(hilos)
for hilo in hilos:
    hilo.start()

# Esperar a que todos terminen
for hilo in hilos:
    hilo.join()

print("\n=========================================================================")
print("\t\t\tSimulación terminada")
print(f"\t\t    De {NUMERO_RATONES_PROBLEMA} ratones, hubo {ratonesRIP} bajas")
print("===========================================================================")
