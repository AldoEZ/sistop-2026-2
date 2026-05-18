#Author: n0tArias

#Para la gente que decidió no leer el README.md y decidió saltarse directamente a ver mi código :moyai:
#Aquí hay una breve descripción de la tarea 3, topes que me encontré y de cómo la implementé.

#Seleccioné el problema del cruce del río, en el que se pretende hacer cruzar a un grupo de personas a un encuentro.

#Este problema se restringe por las siguientes reglas:
#1. La balsa solo puede transportar a 4 personas a la vez, ni más ni menos, de lo contrario, puede volcar.
#2. No pueden existir grupos de 3 personas del mismo tipo en la balsa.
#3. Por consiguiente, no puede existir una sola persona de un tipo en la balsa.
#4. Hay una sola balsa.

#Debido a las primeras 3 reglas, consideré utilizar una barrera para sincronizar a todos los hilos antes de hacer cruzar a la balsa.
#Esto implica el uso de un contador para cada hackers y serfs.
#Para evitar una condición de carrera al acceder a los contadores de hackers y serfs, utilicé un mutex.
#Esto me asegura que las operaciones de incremento y verificación de los contadores sean atómicas, evitando inconsistencias en la formación de grupos.
#También decidí utilizar colas para poder asegurar que se cumplan las reglas 2 y 3, así, cada tipo de hilo espera en su propia cola.
#Estas colas se liberan cuando se forman grupos válidos para poder abordar.
#Con todo esto puedo garantizar que los grupos se forman según las reglas establecidas.
#En el desarrollo, me encontré con el problema de que a veces se creaba una segunda o incluso una tercera balsa.
#Por esto, también me decidí por implementar un semáforo para controlar el comportamiento de la balsa.
#Esto me asegura de que solo un grupo de 4 personas puede abordar y cruzar el río a la vez hasta que la balsa regrese.

from threading import Lock, Barrier, Thread, Semaphore
from time import sleep
from random import shuffle

#El mutex protege el acceso a variables compartidas
#Así evitamos condiciones de carrera
mutex = Lock()

#Contadores para llevar la cuenta de hackers y serfs esperando
hackers = 0
serfs = 0

#Utilizamos colas para controlar el acceso a la balsa
hacker_queue = Semaphore(0)
serf_queue = Semaphore(0)

#Utilizamos barrera para sincronizar a los participantes
#Se optó por una barrera de 4 porque cada cruce requiere que 4 hilos estén listos
#Simplificamos la lógica de sincronización al usar la barrera
barrier = Barrier(4)

#Debido a que solo existe una balsa, se utiliza otro semáforo
#Esto asegura que solo un grupo de 4 personas pueda abordar y cruzar el río a la vez
#Para formar otro grupo, la balsa debe de regresar al muelle
boat_available = Semaphore(1)

#Impresiones para reducir código, mejoramos la legibilidad
def board(tipo):
    print(f"{tipo} está esperando para abordar...")

#Función para simular el cruce del río
#Agregué un retraso para simular el tiempo de abordaje, cruce y retorno de la balsa
def row_boat():
    print("\nIniciando abordaje...\n")
    sleep(0.2)
    print("Todos han abordado, balsa zarpando...\n")
    sleep(0.5)
    print("La balsa llegó a la otra orilla :D\n")
    sleep(0.5)
    print("La balsa regresó al muelle.\n")
    #Este sleep lo agregué para poder leer los mensajes y comprobar que no había errores de sincronización :sob:
    sleep(0.7) 

#Funciones para los hilos de hackers y serfs
#Cada función incrementa su contador correspondiente
#También verifica si el grupo de 4 personas ya está formado
#De ser el caso, entonces libera los semáforos para proceder al abordaje
#Si no, entonces el hilo espera en su semáforo hasta que se forme un grupo
def hacker():
    global hackers, serfs

    with mutex:
        hackers += 1
        if hackers == 4:
            boat_available.acquire()
            hacker_queue.release(4)
            hackers -= 4
        elif hackers == 2 and serfs == 2:
            boat_available.acquire()
            hacker_queue.release(2)
            serf_queue.release(2)
            hackers -= 2
            serfs -= 2

    hacker_queue.acquire()
    board("Hacker")
    index = barrier.wait()

    if index == 0:
        row_boat()
        boat_available.release()


def serf():
    global hackers, serfs

    with mutex:
        serfs += 1
        if serfs == 4:
            boat_available.acquire()
            serf_queue.release(4)
            serfs -= 4
        elif hackers >= 2 and serfs >= 2:
            boat_available.acquire()
            hacker_queue.release(2)
            serf_queue.release(2)
            hackers -= 2
            serfs -= 2

    serf_queue.acquire()
    board("Serf")
    index = barrier.wait()

    if index == 0:
        row_boat()
        boat_available.release()

#Función para solicitar y validar el número de personas a cruzar el río
#Los serfs y hackers deben ser pares para formar grupos de 4
#El total de participantes también debe ser múltiplo de 4 para poder formar grupos con todas las personas
def solicitar_participantes():
    while True:
        n = int(input("Ingrese el número de hackers: "))
        print()
        m = int(input("Ingrese el número de serfs: "))
        print()
        total = n + m
        if total <= 0:
            print("Por favor, ingrese un número positivo de hackers y serfs.")
        elif total % 4 != 0:
            print("El número total de hackers y serfs debe ser múltiplo de 4.")
        elif n % 2 != 0 or m % 2 != 0:
            print("Por favor, ingrese números pares para hackers y serfs.")
        else:
            return n, m

#Función para crear los hilos de hackers y serfs
#Se mezclan los hilos para simular un orden aleatorio de llegada al muelle
def crear_hilos(n_hackers, n_serfs):
    threads = []

    for _ in range(n_hackers):
        threads.append(Thread(target=hacker))

    for _ in range(n_serfs):
        threads.append(Thread(target=serf))

    shuffle(threads)
    return threads

#Función para orquestar la ejecución de los hilos
def ejecutar_cruce(threads):
    #Se ejecutan todos los hilos
    for t in threads:
        t.start()
    #Esperamos a que todos los hilos terminen
    for t in threads:
        t.join()

#Función principal para ejecutar el programa
#Se maneja validación de datos para poder crear los hilos y después ejecutar la lógica del programa
def main():
    n_hackers, n_serfs = solicitar_participantes()
    print("Iniciando el cruce del río...\n")
    threads = crear_hilos(n_hackers, n_serfs)
    ejecutar_cruce(threads)
    print("Todos han cruzado el río exitosamente")

#Entrada del programa, solo lo agrego porque siento que lo hace más legible
if __name__ == "__main__":
    main()
