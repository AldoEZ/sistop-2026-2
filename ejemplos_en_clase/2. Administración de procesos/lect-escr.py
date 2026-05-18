#!/usr/bin/python3

import threading
import time
import random

NUM_LECTORES = 20
NUM_ESCRITORES = 1

pizarron = ''
modo_salon = threading.Semaphore(1)
num_lectores = 0
mutex_num_lectores = threading.Lock()
quiero_pasar = threading.Semaphore(1)

def lector(n):
    global num_lectores
    while True:
        quiero_pasar.acquire()
        quiero_pasar.release()
        with mutex_num_lectores:
            print(f'L{n} ({num_lectores}): ¡Quiero aprender!')
            num_lectores = num_lectores + 1
            if num_lectores == 1:
                modo_salon.acquire()
        print(f'L{n} ({num_lectores}): ¡A aprender!')
        clase = lee()
        print(f'L{n} ({num_lectores}): Aprendí {clase}')
        time.sleep(random.random())
        with mutex_num_lectores:
            print(f'L{n} ({num_lectores}): Me fui.')
            num_lectores = num_lectores - 1
            if num_lectores == 0:
                modo_salon.release()
        time.sleep(random.random())

def escritor(n):
    while True:
        clase = random.random()
        print(f'       E{n}: ¡Quiero escribir!')
        quiero_pasar.acquire()
        modo_salon.acquire()
        print(f'       E{n}: Entrando...')
        escribe(clase)
        print(f'       E{n}: Escribí {clase}')
        time.sleep(5*random.random())
        modo_salon.release()
        quiero_pasar.release()
        time.sleep(0.1 * random.random())

def lee():
    global pizarron
    time.sleep(0.1 * random.random())
    return pizarron

def escribe(que):
    global pizarron
    time.sleep(random.random())
    pizarron = que

for i in range(NUM_ESCRITORES):
    threading.Thread(target=escritor, args=[i]).start()

for i in range(NUM_LECTORES):
    threading.Thread(target=lector, args=[i]).start()
