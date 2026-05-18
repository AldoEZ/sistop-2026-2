#!/usr/bin/python3
from threading import Thread, Semaphore, Barrier
from time import sleep

NUM_HILOS = 10
barrera = Barrier(NUM_HILOS)

def hilo(n):
    print(f'{n}: se dispone a hacer su trabajo...')
    barrera.wait()
    print(f'{n}: ¡Por fin pude pasar!')

for i in range(30):
    Thread(target=hilo, args=[i]).start()
    sleep(1)
