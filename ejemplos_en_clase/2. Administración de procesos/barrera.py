#!/usr/bin/python3
from threading import Thread, Semaphore
from time import sleep

NUM_HILOS = 10
barrera = Semaphore(0)
mutex = Semaphore(1)
contador = 0

def hilo(n):
    global contador
    print(f'{n}: se dispone a hacer su trabajo...')
    mutex.acquire()
    contador = contador + 1
    if contador == NUM_HILOS:
        barrera.release()
    mutex.release()
    barrera.acquire()
    barrera.release()
    print(f'{n}: ¡Por fin pude pasar!')

for i in range(30):
    Thread(target=hilo, args=[i]).start()
    sleep(1)
