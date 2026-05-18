#!/usr/bin/python3

import threading
import time
import random

NUM_PROD = 3
NUM_CONS = 4
MAX_COSAS = 4

mutex = threading.Semaphore(1)
hay_cosas = threading.Semaphore(0)
max_cosas = threading.Semaphore(MAX_COSAS)
cinta = []

# productor  →   función (utliza mutex, cinta, ...?)
# consumidor →   función (utliza mutex, cinta, ...?)
# objeto     →   variable, “habitante” de la cinta
# cinta      →   arreglo

def productor(n):
    global mutex, cinta
    while True:
        time.sleep(random.random())
        cosa = random.random()
        print(f'P{n}: Produciendo cosa: {cosa}')
        max_cosas.acquire()
        mutex.acquire()
        cinta.append(cosa)
        mutex.release()
        hay_cosas.release()

def consumidor(n):
    global mutex, cinta
    while True:
        time.sleep(random.random())
        hay_cosas.acquire()
        mutex.acquire()
        cosa = cinta.pop()
        print(f'C{n}: La cinta tiene {len(cinta)} elementos.')
        mutex.release()
        max_cosas.release()
        print(f'C{n}: Procesando cosa: {cosa}')

for i in range(NUM_PROD):
    threading.Thread(target=productor, args=[i]).start()

for i in range(NUM_CONS):
    threading.Thread(target=consumidor, args=[i]).start()
