import random
import copy

class Proceso:
	def __init__(self, nombre, llegada, t):
		self.nombre = nombre
		self.llegada = llegada
		self.t = t
		self.falta = t ##Tiempo faltante (Utilizado para rr)


	def to_string(self):
		return "Proceso: " + str(self.nombre) + " llegada: " + str(self.llegada) + " t:" + str(self.t)

#Crea procesos aleatorios
def crear_proecesos(n):
	P = []

	for i in range(n):
		P.append(Proceso(chr(65+i), random.randint(0,5), random.randint(2,6)))


	#Regresa la lista de procesos ordenada según su tiempo de llegada para simular la llegada real de procesos
	return sorted(P, key= lambda x: x.llegada)


def FCFS(procesos):
	tiempo = 0
	inicio = 0
	orden_procesos = ""
	metricas = {}
	T_t=0
	E_t=0
	P_t=0

	for p in procesos:

		if tiempo < p.llegada:
			tiempo = p.llegada

		inicio = tiempo
		for _ in range(p.t):
			orden_procesos+=p.nombre
			tiempo+=1

		fin = tiempo
		T = fin - p.llegada
		E = T - p.t
		P = T/p.t

		#Calculo de metricas totales
		T_t += T
		E_t += E
		P_t += P

	#Lista de métricas
	total_procesos = len(procesos)
	metricas = {"T" : T_t/total_procesos, "E" : E_t/total_procesos, "P" : P_t/total_procesos}

	return metricas, orden_procesos

def RR(procesos, quantum):
	tiempo = 0
	cola = []
	metricas = {}
	orden_procesos = ""
	i = 0
	T_t = 0
	E_t = 0
	P_t = 0

	#Permite crear una copia de la lista de procesos para modificarla sin afectar al original
	process = copy.deepcopy(procesos)
	


	while cola or i < len(process):

		while i < len(process) and process[i].llegada <= tiempo:
			cola.append(process[i])
			i += 1

		if cola:
			p = cola.pop(0)
			tiempo_ejecutado = 0

			while tiempo_ejecutado < quantum and p.falta > 0:
				orden_procesos += p.nombre
				p.falta -= 1
				tiempo += 1
				tiempo_ejecutado += 1

				while i < len(process) and process[i].llegada <= tiempo:
					cola.append(process[i])
					i += 1

			if p.falta > 0:
				cola.append(p)
			else:
				T = tiempo - p.llegada
				E = T - p.t
				P = T / p.t

				T_t += T
				E_t += E
				P_t += P
		else:
			tiempo += 1

	total_procesos = len(process)
	metricas = {"T" : T_t/total_procesos, "E" : E_t/total_procesos, "P" : P_t/total_procesos}

	return metricas, orden_procesos

def SPN(procesos):
    tiempo = 0
    completados = 0
    n = len(procesos)
    orden_procesos = ""
    T_t = 0
    E_t = 0
    P_t = 0

	#Permite crear una copia de la lista de procesos para modificarla sin afectar al original
    process = copy.deepcopy(procesos)
    #Permite saber qué procesos ya han terminado
    terminados = [False] * n

    while completados < n:
        disponibles = []

        # Busca procesos que llegaron y no han terminado
        for i in range(n):
            if process[i].llegada <= tiempo and not terminados[i]:
                disponibles.append((i, process[i]))

        if disponibles:
            # Elegir el de menor tiempo t
            i_min, p = min(disponibles, key=lambda x: x[1].t)

            # Ejecución completa del proceso
            for _ in range(p.t):
                orden_procesos += p.nombre
                tiempo += 1

            # Calculando métricas
            fin = tiempo
            T = fin - p.llegada
            E = T - p.t
            P = T / p.t

            T_t += T
            E_t += E
            P_t += P

            terminados[i_min] = True
            completados += 1

        else:
            # Si no hay procesos disponibles, avanza el tiempo
            tiempo += 1

    metricas = {
        "T": T_t / n,
        "E": E_t / n,
        "P": P_t / n
    }

    return metricas, orden_procesos


def iniciar():
	#Primer proceso igual al del ejemplo de la asignación:

	print("Primera ejecución: Ejemplo de la asignacion")
	print("Procesos")
	P = [Proceso('A', 0,3),Proceso('B', 1,5),Proceso('C', 3,2),
	Proceso('D', 9,5), Proceso('E', 12,5)]
	for j in range(len(P)):
			print(P[j].to_string())
	metricas, orden_procesos = FCFS(P) 
	print(f'FCFS:{metricas}')
	print(f'{orden_procesos}')	

	metricas, orden_procesos = RR(P,1)
	print(f'RR1:{metricas}')
	print(f'{orden_procesos}')

	metricas, orden_procesos = RR(P,4)
	print(f'RR4:{metricas}')
	print(f'{orden_procesos}')

	metricas, orden_procesos = SPN(P)
	print(f'SPN:{metricas}')
	print(f'{orden_procesos}')

	print()

	#Procesos aleatorios: 

	for i in range(4):
		print(f'Ronda {i+2}:')
		P = crear_proecesos(5)
		print("Procesos generados")
		for j in range(len(P)):
			print(P[j].to_string())

		print()

		metricas, orden_procesos = FCFS(P) 
		print(f'FCFS:{metricas}')
		print(f'{orden_procesos}')	

		metricas, orden_procesos = RR(P,1)
		print(f'RR1:{metricas}')
		print(f'{orden_procesos}')

		metricas, orden_procesos = RR(P,4)
		print(f'RR4:{metricas}')
		print(f'{orden_procesos}')

		metricas, orden_procesos = SPN(P)
		print(f'SPN:{metricas}')
		print(f'{orden_procesos}')

		print ()

iniciar()


