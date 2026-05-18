## Tarea 03. Comparacion de planificadores
# Autores:
# Bello Sanchez Santiago Arath
# López Romero David Baruc
# ##

import random
import string

class Process:
    def __init__(self, pid, arrival, duration):
        self.pid = pid #id del proceso
        self.arrival = arrival #Milisegundo de entrada al sistema
        self.duration = duration
        #Cambiasntes durante la ejecucion:
        self.remaining = duration #Cuanto tiempo le FALTA por ejecutar
        self.finish_time = 0 #Milisegundo en que termina por completo
        self.level = 0  # Usado para el algoritmo FB

#Copia de los procesos
#Asi un algoritmo no modifica datos de otro
def copy_work(workload):
    return [Process(p.pid, p.arrival, p.duration) for p in workload]

def simulate(workload, algo="FCFS"):
    procs = copy_work(workload)
    t = 0   #Tiempo actual del sistema
    gantt = ""
    running = None  #Proceso ejecutandose actualmente
    q_ticks = 0
    
    # Colas para los distintos algoritmos
    ready = []
    fb_queues = {i: [] for i in range(20)} # Hasta 20 niveles de prioridad para FB
    
    # Extraer el quantum si es RR
    q = 1
    if algo.startswith("RR"):
        q = int(algo[2:])

    while len([p for p in procs if p.remaining > 0]) > 0:
        # 1. Llegada de procesos en el instante 't'
        for p in procs:
            if p.arrival == t:
                if algo == "FB":
                    fb_queues[0].append(p)  #Cola para FB (nivel 0, mayor prioridad)
                else:
                    ready.append(p) #Cola general

        # 2. Selección del siguiente proceso si la CPU está inactiva
        if not running:
            #Firs-Come, First-Served. El primero en llegar a la cola pasa
            if algo == "FCFS" and ready:
                ready.sort(key=lambda x: x.arrival)
                running = ready.pop(0)
            #Shortest Process Next. Pasa quien tenga la duracion total mas corta
            elif algo == "SPN" and ready:
                ready.sort(key=lambda x: x.duration)
                running = ready.pop(0)
            #Round RObin. Pasa quien esta delante en la cola y se reinicia su reloj
            elif algo.startswith("RR") and ready:
                running = ready.pop(0)
                q_ticks = 0
            #Feedback. Se busca de arriba abajo en la cola multinivel
            elif algo == "FB":
                for level in range(20):
                    if fb_queues[level]:
                        running = fb_queues[level].pop(0)
                        q_ticks = 0
                        break

        # 3. Ejecución de 1 unidad de tiempo (tick)
        if running:
            running.remaining -= 1
            q_ticks += 1
            gantt += running.pid

            # Finalización del proceso
            if running.remaining == 0:
                running.finish_time = t + 1
                running = None
            # Expiración de Quantum en Round Robin
            elif algo.startswith("RR") and q_ticks == q:
                ready.append(running)
                running = None
            # Expiración de Quantum y degradación en Feedback (FB)
            elif algo == "FB" and q_ticks == 1:
                running.level += 1
                fb_queues[running.level].append(running)
                running = None
        else:
            # Si no hay procesos listos pero aún faltan por llegar
            if any(p.arrival > t for p in procs):
                gantt += "-"

        t += 1

    # 4. Cálculo de métricas
    tot_T = tot_E = tot_P = 0
    n = len(procs)
    for p in procs:
        T = p.finish_time - p.arrival
        E = T - p.duration
        P = T / p.duration
        tot_T += T; tot_E += E; tot_P += P
        
    return f"{algo:<5}: T={tot_T/n:.2f}, E={tot_E/n:.2f}, P={tot_P/n:.2f}\n      {gantt}"

#Main function, genera las tareas aleatorias
def run_simulation(rounds=5):
    pids = list(string.ascii_uppercase)#['A','B', ...]
    
    for rnd in range(1, rounds + 1):
        print(f"- Ronda {rnd}:")
        
        # Generar carga aleatoria (5 procesos)
        workload = []
        arrival = 0
        tot_duration = 0
        for i in range(5):
            duration = random.randint(2, 7)
            workload.append(Process(pids[i], arrival, duration))
            tot_duration += duration
            arrival += random.randint(0, 3) # Los procesos llegan muy cerca unos de otros
            
        # Imprimir encabezado de la carga
        header = "; ".join([f"{p.pid}: {p.arrival}, t={p.duration}" for p in workload])
        print(f"  {header} (tot:{tot_duration})")
        
        # Ejecutar y comparar algoritmos
        algos = ["FCFS", "RR1", "RR4", "SPN", "FB"]
        for algo in algos:
            print(f"  {simulate(workload, algo)}")
        print()

if __name__ == "__main__":
    run_simulation(5)