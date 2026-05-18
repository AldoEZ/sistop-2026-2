#!/usr/bin/python3
from threading import Thread, Semaphore
from time import sleep
import datetime

torniquete = Semaphore(0)

def hilo(n):
    print(f'{n}: se dispone a hacer su trabajo...')
    ahora = datetime.datetime.now()
    if ahora.second % 10 == 0:
        torniquete.release()
        print(ahora)
    torniquete.acquire()
    torniquete.release()
    print(f'{n}: ¡Por fin pude pasar!')

for i in range(30):
    Thread(target=hilo, args=[i]).start()
    sleep(1)
