#!/usr/bin/python3

import time
import random
import threading

NUM_FILOSOFOS = 5
mult = threading.Semaphore( NUM_FILOSOFOS - 1 )
sem_palillos = [ threading.Semaphore(1) for i in range(NUM_FILOSOFOS) ]

def _yo(x, msg):
    print('%s%d: %s' % (' '*x, x, msg) )

def piensa(x):
    _yo(x, 'Comienzo a pensar')
    _yo(x, 'Ya pensé lo suficiente.')

def come(x):
    _yo(x, 'Tengo hambre 🙁')
    levanta_palillos(x)
    _yo(x, '¡A comer! 🍚')
    _yo(x, '¡Qué rico arroz! 😛')
    deja_palillos(x)

def levanta_palillos(x):
    mult.acquire()
    sem_palillos[x].acquire()
    sem_palillos[ (x+1) % NUM_FILOSOFOS ].acquire()

def deja_palillos(x):
    sem_palillos[x].release()
    sem_palillos[ (x+1) % NUM_FILOSOFOS ].release()
    mult.release()

def filosofo(x):
    while True:
        piensa(x)
        come(x)

for i in range(NUM_FILOSOFOS):
    threading.Thread(target=filosofo, args=[i]).start()
