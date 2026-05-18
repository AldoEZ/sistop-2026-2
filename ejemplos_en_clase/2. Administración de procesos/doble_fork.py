#!/usr/bin/python3
import os
import time

# Aquí vamos a hacer un doble fork() para lanzar un proceso servidor, y no
# vamos a esperar a su SIGCHLD

pid = os.fork()

if pid == 0:
    # Proceso hijo
    pid = os.fork()
    if pid == 0:
        # Proceso hijo-segundo
        time.sleep(1)
        print('Ahora yo soy hijo del PID 1:')
        pid = os.getpid()
        ppid = os.getppid()
        print(f'Mi PID es {pid}, el de mi padre es {ppid}')
        while True:
            time.sleep(1)
exit()
