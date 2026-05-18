#!/usr/bin/env python3

import threading

hilos=[]

def crear_archivo(numHilo):
	print(f"Soy el hilo {numHilo}")
	with open("archivoHilos.txt", "a") as f:
		f.write(f"Cantidad de hilos final: {len(hilos)}\n")

for i in range(5):
	hilo=threading.Thread(target=crear_archivo, args=[i])
	hilos.append(hilo)

for hilo in hilos:
	hilo.start()
