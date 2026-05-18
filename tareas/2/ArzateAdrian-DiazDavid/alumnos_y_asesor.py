#!/usr/bin/env python3

import threading as th
import random
import time

numero_sillas = 10

maximo_dudas = 10


class Alumno(th.Thread):
	# Constructor de la clase Alumno
	def __init__(self, id, sillas, turno, condicion):
		super().__init__()
		self.id = id
		self.silla = sillas
		self.turno = turno
		self.condicion = condicion
		self.numero_dudas = random.randint(1, maximo_dudas) # una cantidad de dudas aleatoria entre 1 y maximo_dudas

	# comportamiento del hilo Alumno
	def run(self):
		with self.silla:

			print(f"El alumno {self.id} entró al cubiculo")

			self.resolver_dudas()

		print(f"El alumno {self.id} salió del cubiculo")

	# Resolucion de dudas
	def resolver_dudas(self):
		while self.numero_dudas != 0:
			
			with self.turno:
				self.condicion.notify()
				print(f"El alumno {self.id} está resolviendo una duda")
				self.condicion.wait()
				self.numero_dudas -= 1
							
			time.sleep(1)

		print(f"El alumno {self.id} resolvio todas sus dudas") 

class Profesor(th.Thread):
	# Constructor de la clase Profesor
	def __init__(self, condicion):
		super().__init__()
		self.condicion = condicion

	# comportamiento del hilo profesor
	def run(self):
		with self.condicion:
			while True:
				self.condicion.wait()
				print(f"El Profesor está resolviendo una duda")
				
				time.sleep(1)

				self.condicion.notify()
				print(f"El Profesor terminó con una duda")		

def main():
	global numero_sillas
	# semaforo del numero de sillas
	numero_sillas = th.Semaphore(numero_sillas)
	# mutex 
	turno = th.Lock()
	# condicion de espera (dormir)
	condicion = th.Condition(turno)
	# inicializacion de los identificadores de los alumnos
	id_alumno = 1	
	# se crea el hilo profesor
	profesor = Profesor(condicion)
	profesor.daemon = True # para detener el hilo cuando no hayan mas alumnos
	profesor.start() # se inicializa el hilo


	try:
		# bucle principal
		while True:
			#creacion indeterminada de alumnos
			alumno = Alumno(id_alumno, numero_sillas, turno, condicion)
			alumno.start() # inicializacion de cada alumno
			id_alumno += 1 # conteo de la id de los alumnos
			time.sleep(3) # retraso en el tiempo para que las salidas en consola sean legibles
	except KeyboardInterrupt: # ctrl + c para terminar el programa
		print("finalizacion")


main()
