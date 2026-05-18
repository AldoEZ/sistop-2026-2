#!/usr/bin/python3
import signal
import os
import time


def handler(signum, frame):
    if signum == signal.SIGCHLD:
        os.waitpid(-1, os.WNOHANG)
        print(f'Terminé de esperar a un proceso hijo: {signum}, {frame}')
    elif signum == signal.SIGINT:
        print('OK, ya me voy — Pero me voy limpiamente.')
        exit(0)
    elif signum == signal.SIGWINCH:
        print('Cambió la geometría de la ventana...')
    elif signum == signal.SIGUSR1:
        print('¿Y qué quiere este usuario latoso?')

signal.signal(signal.SIGCHLD, handler)
signal.signal(signal.SIGINT, handler)
signal.signal(signal.SIGWINCH, handler)
signal.signal(signal.SIGUSR1, handler)

pid = os.getpid()
ppid = os.getppid()

print(f'El PID de este proceso es {pid}, y papá es el {ppid}')

nvo_pid = os.fork()
print('¡Ya hice mi fork()!')
pid = os.getpid()

if nvo_pid == 0:
    # Soy el proceso hijo
    print(f'Soy el proceso hijo ({nvo_pid}). Mi PID es: {pid}')
    time.sleep(2)
    print('Ya me aburrí. Me voy.')
elif nvo_pid > 0:
    # Soy el proceso padre
    print(f'Soy el proceso padre ({nvo_pid}). Mi PID es: {pid}')
    while True:
        time.sleep(1)
else:
    # Ocurrió un error
    print(f'¡Algo salió mal! ¡El mundo se incendia! {nvo_pid}')

