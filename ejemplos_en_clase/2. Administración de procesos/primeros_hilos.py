#!/usr/bin/python3
import threading
from time import sleep

hilos = []

def mi_hilo(num):
    global hilos
    print(f'Soy {num}. Hay {len(hilos)}.')
    for i in range(5):
        print(num)
        sleep(1)

for i in range(4):
    hilo = threading.Thread(target = mi_hilo, args = [i])
    hilos.append(hilo)

for hilo in hilos:
    hilo.start()

print('Esperemos a que todos terminen...')
for hilo in hilos:
    hilo.join()
print('Listo, ya terminaron. Todos.')
