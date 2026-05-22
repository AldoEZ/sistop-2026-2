#!/usr/bin/env python3
#este es el shebang. Le dice a Linux/Mac que ejecute este archivo usando Python 3

from __future__ import annotations
from dataclasses import dataclass
from collections import deque
from typing import List, Dict, Tuple, Optional
import argparse
import random

#constantes para el algoritmo Feedback (FB)
FB_LEVELS = 3 # Tendremos 3 colas de distinta prioridad
FB_QUANTA = (1, 2, 4) # El quantum para la cola 0 es 1, para la cola 1 es 2, y para la cola 2 es 4

# Esta clase solo guarda los datos originales del proceso 
# Usamos frozen=True para que nadie modifique por error la llegada o el total original.
@dataclass(frozen=True)
class ProcSpec:
    name: str
    arrival: int
    total: int

# esta clase es el estado actual del proceso. Aqui sí vamos a ir restando el tiempo 
# que le falta, anotando en qué tick terminó y en qué nivel de cola de Feedback esta
@dataclass
class ProcState:
    name: str
    arrival: int
    total: int
    remaining: int
    finish: Optional[int] = None
    level: int = 0

# una estructura para empaquetar toda la basura que devuelve la simulacion
# así no tenemos funciones regresando 10 variables sueltas.
@dataclass
class AlgoResult:
    algo: str
    timeline: str
    per_proc: Dict[str, Dict[str, float]]
    avg_T: float
    avg_E: float
    avg_P: float
    makespan: int

#esta función dibuja la regla superior (t: 0....5....10) para no perdernos contando letras
def build_time_rule(makespan: int) -> str:
    if makespan <= 0: return "t: "
    chars = ['.'] * makespan
    for k in range(0, makespan, 5):
        s = str(k)
        for j, ch in enumerate(s):
            if k + j < makespan: chars[k + j] = ch
    return "t: " + ''.join(chars)

# Una vez que la simulación termina, esta función calcula T, E y P usando
# las fórmulas vistas en clase También saca los promedios globales.
def compute_metrics(states: Dict[str, ProcState]) -> Tuple[Dict[str, Dict[str, float]], float, float, float]:
    per, Ts, Es, Ps = {}, [], [], []
    for name in sorted(states.keys()):
        p = states[name]
        a, t, f = p.arrival, p.total, p.finish
        T = f - a       # Tiempo de estancia (Turnaround) = Fin - Llegada
        E = T - t       # Tiempo de espera = Estancia - Ráfaga de CPU
        P = T / t       # indice de penalización = Estancia / Ráfaga
        per[name] = {"a": a, "t": t, "f": f, "T": T, "E": E, "P": P}
        Ts.append(T); Es.append(E); Ps.append(P)
    
    n = len(states)
    return per, sum(Ts)/n, sum(Es)/n, sum(Ps)/n

# Crea diccionarios mutables a partir de los datos originales
def init_states(specs: List[ProcSpec]) -> Dict[str, ProcState]:
    return {s.name: ProcState(s.name, s.arrival, s.total, s.total) for s in specs}

# Revisa la lista de procesos y nos devuelve solo los que acaban de llegar en este instante t
def arrivals_at(specs: List[ProcSpec], t: int) -> List[ProcSpec]:
    return [s for s in specs if s.arrival == t]

#checa si todos los procesos ya tienen anotado su tiempo de fin
def all_done(states: Dict[str, ProcState]) -> bool:
    return all(p.finish is not None for p in states.values())

#simulacion fcs en donde el primer en llegar lo atienden primero
def simulate_fcfs(specs: List[ProcSpec]) -> AlgoResult:
    states = init_states(specs)
    ready = deque() # Cola de listos
    running = None  # quien tiene la CPU ahorita
    timeline = []   # Historial Visual 
    t = 0           # tick actual
    
    while not all_done(states):
        #Metemos a la cola a los que van llegando, ordenados alfabéticamente si hay empate
        for s in sorted(arrivals_at(specs, t), key=lambda x: x.name):
            ready.append(s.name)
            
        #Si la CPU está libre y hay gente esperando, metemos al primero de la cola
        if running is None and ready:
            running = ready.popleft()
            
        #Ejecución del tick
        if running is None: 
            timeline.append('_') 
        else:
            timeline.append(running)
            p = states[running]
            p.remaining -= 1
            # Si el proceso ya agotó su tiempo, lo marcamos como terminado
            if p.remaining == 0:
                p.finish = t + 1 # Termina en el siguiente tick cronológico
                running = None
        t += 1 # Avanzamos el reloj
        
    per, aT, aE, aP = compute_metrics(states)
    return AlgoResult("FCFS", ''.join(timeline), per, aT, aE, aP, len(timeline))

# simulación round robin pero que pondremos como 'rr'
def simulate_rr(specs: List[ProcSpec], q: int) -> AlgoResult:
    states = init_states(specs)
    ready = deque()
    running = None
    qleft = 0 # El contador de quantum, cuánto tiempo le queda al proceso actual en la CPU
    timeline = []
    t = 0
    
    while not all_done(states):
        # encolamos a los recién llegados
        for s in sorted(arrivals_at(specs, t), key=lambda x: x.name):
            ready.append(s.name)
            
        # Si la CPU está libre, agarramos uno y le damos su quantum completo
        if running is None and ready:
            running = ready.popleft()
            qleft = q 
            
        # ejecutando
        if running is None: 
            timeline.append('_')
        else:
            timeline.append(running)
            p = states[running]
            p.remaining -= 1
            qleft -= 1
            
            # se verifica por qué debe salir de la CPU
            if p.remaining == 0:
                # Terminó su tarea antes o al mismo tiempo que el quantum
                p.finish = t + 1
                running, qleft = None, 0
            elif qleft == 0:
                # Se le acabó el tiempo, se expropia y va al final de la cola
                ready.append(running)
                running = None
                
        t += 1
        
    per, aT, aE, aP = compute_metrics(states)
    return AlgoResult(f"RR{q}", ''.join(timeline), per, aT, aE, aP, len(timeline))

#SPn el corto va primero
def simulate_spn(specs: List[ProcSpec]) -> AlgoResult:
    states = init_states(specs)
    ready = [] # usamos lista normal porque vamos a reordenarla constantemente
    running = None
    timeline = []
    t = 0
    
    while not all_done(states):
        for s in sorted(arrivals_at(specs, t), key=lambda x: x.name):
            ready.append(s.name)
            
        if running is None and ready:
            # Ordenamos a los listos buscando al de menor ráfaga total
            # Si empatan en ráfaga, desempatamos por tiempo de llegada, y luego por nombre
            ready.sort(key=lambda n: (states[n].total, states[n].arrival, n))
            running = ready.pop(0)
            
        if running is None: 
            timeline.append('_')
        else:
            timeline.append(running)
            p = states[running]
            p.remaining -= 1
            # Como SPN no expropia, se queda hasta que termina su ráfaga
            if p.remaining == 0:
                p.finish = t + 1
                running = None
                
        t += 1
        
    per, aT, aE, aP = compute_metrics(states)
    return AlgoResult("SPN", ''.join(timeline), per, aT, aE, aP, len(timeline))

# COlas multinivel con penalización 
def simulate_fb(specs: List[ProcSpec]) -> AlgoResult:
    states = init_states(specs)
    # Creamos un arreglo con 3 colas distintas una para cada nivel
    qs = [deque() for _ in range(FB_LEVELS)]
    running = None
    qleft = 0
    timeline = []
    t = 0
    
    # Función de ayuda que busca al siguiente proceso revisando primero la cola 0, luego la 1 y al final la 2
    def pick_next():
        for lvl in range(FB_LEVELS):
            if qs[lvl]:
                n = qs[lvl].popleft()
                states[n].level = lvl
                return n
        return None

    while not all_done(states):
        # Los nuevos siempre entran por la cola VIP en el nivel 0
        for s in sorted(arrivals_at(specs, t), key=lambda x: x.name):
            states[s.name].level = 0
            qs[0].append(s.name)
            
        # Expropiación estricta por prioridad: si hay alguien corriendo que no es VIP, nivel > 0
        # y acaba de llegar alguien a la cola VIP qs[0], le quitamos la CPU inmediatamente.
        if running is not None and states[running].level > 0 and qs[0]:
            qs[states[running].level].append(running)
            running, qleft = None, 0
            
        # asignar CPU al de mayor prioridad disponible
        if running is None:
            running = pick_next()
            # Le damos el quantum correspondiente al nivel en el que estaba
            if running: qleft = FB_QUANTA[states[running].level]
            
        # ejecutando
        if running is None: 
            timeline.append('_')
        else:
            timeline.append(running)
            p = states[running]
            p.remaining -= 1
            qleft -= 1
            
            # la salida de la CPU
            if p.remaining == 0:
                p.finish = t + 1
                running, qleft = None, 0
            elif qleft == 0:
                # se le acabó el quantum. La penalización consiste en que lo mandamos a un nivel inferior o número mayor.
                # Usamos min() para que si ya está en la última cola, no se salga del arreglo
                p.level = min(p.level + 1, FB_LEVELS - 1)
                qs[p.level].append(p.name)
                running = None
                
        t += 1
        
    per, aT, aE, aP = compute_metrics(states)
    return AlgoResult("FB", ''.join(timeline), per, aT, aE, aP, len(timeline))

# Esta función se encarga exclusivamente de darle formato bonito a la salida
def print_algo(res: AlgoResult):
    # Imprime promedios globales del algoritmo
    print(f"\n{res.algo}: T={res.avg_T:.2f}, E={res.avg_E:.2f}, P={res.avg_P:.2f}")
    # Imprime línea de tiempo visual
    print(build_time_rule(res.makespan))
    print("run: " + res.timeline)
    # Imprime desglose individual
    for name in sorted(res.per_proc.keys()):
        d = res.per_proc[name]
        print(f"{name} a={int(d['a'])} t={int(d['t'])} f={int(d['f'])} T={int(d['T'])} E={int(d['E'])} P={d['P']:.2f}")

def main():
    # Usamos argparse para poder pasarle variables desde la terminal
    ap = argparse.ArgumentParser()
    ap.add_argument('--rondas', type=int, default=5)
    ap.add_argument('--nproc', type=int, default=5)
    ap.add_argument('--seed', type=int, default=123)
    args = ap.parse_args()

    # Semilla para que los números aleatorios sean los mismos si usamos la misma semilla
    rng = random.Random(args.seed)
    
    # Ciclo principal que corre las 5 rondas solicitadas
    for r in range(1, args.rondas + 1):
        # Generamos los 5 procesos con llegadas y tiempos aleatorios
        specs = sorted([ProcSpec(chr(65+i), rng.randint(0,12), rng.randint(2,7)) for i in range(args.nproc)], key=lambda x: x.name)
        
        # Formato de cabecera como lo pidió el profesor en la rúbrica
        tot = sum([p.total for p in specs])
        proc_str = "; ".join([f"{p.name}: {p.arrival}, t={p.total}" for p in specs])
        print(f"\n- Ronda {r}:")
        print(f"  {proc_str} (tot:{tot})")
        
        # Ejecutamos todos los algoritmos con la misma carga de procesos de esta ronda
        algos = [
            simulate_fcfs(specs), 
            simulate_rr(specs, 1), # Quantum duro de 1
            simulate_rr(specs, 4), # Quantum duro de 4
            simulate_spn(specs), 
            simulate_fb(specs)
        ]
        
        # Imprimimos resultados de todos los algoritmos
        for res in algos: 
            print_algo(res)

if __name__ == '__main__':
    main()

