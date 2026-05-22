import random
import sys
from collections import deque


# Generacion de procesos aleatorios
# Cada proceso es un diccionario con nombre, tiempo de llegada y duracion

LETRAS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def genera_procesos(n=5):
    procs = []
    llegada = 0
    for k in range(n):
        if k > 0:
            llegada += random.randint(0, 4)
        duracion = random.randint(2, 7)
        procs.append({"nombre": LETRAS[k],
                      "llegada": llegada,
                      "t": duracion})
    return procs


def resumen_procesos(procs):
    partes = [f"{p['nombre']}: {p['llegada']}, t={p['t']}" for p in procs]
    total = sum(p["t"] for p in procs)
    return "; ".join(partes) + f" (total:{total})"



# Calculo de metricas a partir de la traza de ejecucion
# Regresa promedios de T, E y P

def metricas(procs, traza):
    fin = {}
    for i, nm in enumerate(traza):
        if nm != "-":
            fin[nm] = i + 1
    sumaT = sumaE = sumaP = 0.0
    for p in procs:
        T = fin[p["nombre"]] - p["llegada"]
        E = T - p["t"]
        P = T / p["t"]
        sumaT += T
        sumaE += E
        sumaP += P
    n = len(procs)
    return sumaT / n, sumaE / n, sumaP / n


# FCFS - primero en llegar, primero en atenderse.

def fcfs(procs):
    orden = sorted(procs, key=lambda p: p["llegada"])
    traza = []
    reloj = 0
    for p in orden:
        if reloj < p["llegada"]:
            traza += ["-"] * (p["llegada"] - reloj)
            reloj = p["llegada"]
        traza += [p["nombre"]] * p["t"]
        reloj += p["t"]
    return traza


# Round Robin con cuanto q
# Cuando un proceso agota su cuanto, los recien llegados entran a la cola antes de re-encolar al que acaba de correr

def round_robin(procs, q):
    pend = sorted(procs, key=lambda p: p["llegada"])
    cola = deque()
    restante = {p["nombre"]: p["t"] for p in procs}
    traza = []
    reloj = 0
    idx = 0
    while idx < len(pend) or cola:
        while idx < len(pend) and pend[idx]["llegada"] <= reloj:
            cola.append(pend[idx])
            idx += 1
        if not cola:
            traza.append("-")
            reloj += 1
            continue
        p = cola.popleft()
        ciclos = min(q, restante[p["nombre"]])
        for _ in range(ciclos):
            traza.append(p["nombre"])
            reloj += 1
            while idx < len(pend) and pend[idx]["llegada"] <= reloj:
                cola.append(pend[idx])
                idx += 1
        restante[p["nombre"]] -= ciclos
        if restante[p["nombre"]] > 0:
            cola.append(p)
    return traza


# SPN - shortest process next
# De los procesos que ya llegaron, se elige el de menor duracion total

def spn(procs):
    pend = sorted(procs, key=lambda p: p["llegada"])
    traza = []
    reloj = 0
    hechos = set()
    while len(hechos) < len(procs):
        listos = [p for p in pend
                  if p["llegada"] <= reloj and p["nombre"] not in hechos]
        if not listos:
            traza.append("-")
            reloj += 1
            continue
        p = min(listos, key=lambda x: x["t"])
        traza += [p["nombre"]] * p["t"]
        reloj += p["t"]
        hechos.add(p["nombre"])
    return traza



# FB - retroalimentacion multinivel
# Varias colas numeradas, 0 es la de mayor prioridad

def fb(procs, niveles=4):
    pend = sorted(procs, key=lambda p: p["llegada"])
    colas = [deque() for _ in range(niveles)]
    restante = {p["nombre"]: p["t"] for p in procs}
    traza = []
    reloj = 0
    idx = 0
    total = len(procs)
    terminados = 0
    while terminados < total:
        while idx < len(pend) and pend[idx]["llegada"] <= reloj:
            colas[0].append(pend[idx])
            idx += 1
        nivel = next((k for k in range(niveles) if colas[k]), None)
        if nivel is None:
            traza.append("-")
            reloj += 1
            continue
        p = colas[nivel].popleft()
        traza.append(p["nombre"])
        reloj += 1
        restante[p["nombre"]] -= 1
        while idx < len(pend) and pend[idx]["llegada"] <= reloj:
            colas[0].append(pend[idx])
            idx += 1
        if restante[p["nombre"]] == 0:
            terminados += 1
        else:
            destino = min(nivel + 1, niveles - 1)
            colas[destino].append(p)
    return traza


# SRR - ronda egoista (selfish round robin)
# Hay dos colas logicas: nuevos y aceptados

def srr(procs, a=2, b=1):
    pend = sorted(procs, key=lambda p: p["llegada"])
    nuevos = []          # pares [nombre, prioridad]
    aceptados = deque()
    restante = {p["nombre"]: p["t"] for p in procs}
    traza = []
    reloj = 0
    idx = 0
    total = len(procs)
    terminados = 0
    prio_acept = 0
    while terminados < total:
        while idx < len(pend) and pend[idx]["llegada"] <= reloj:
            nuevos.append([pend[idx]["nombre"], 0])
            idx += 1
        # Promocion de nuevos que alcanzaron la prioridad de los aceptados
        restan = []
        for par in nuevos:
            if not aceptados or par[1] >= prio_acept:
                aceptados.append(par[0])
            else:
                restan.append(par)
        nuevos = restan
        # Ejecucion de un tick
        if not aceptados:
            traza.append("-")
            reloj += 1
        else:
            nm = aceptados.popleft()
            traza.append(nm)
            restante[nm] -= 1
            reloj += 1
            if restante[nm] == 0:
                terminados += 1
            else:
                aceptados.append(nm)
        # Ajuste de prioridades al cerrar el tick
        for par in nuevos:
            par[1] += a
        if aceptados:
            prio_acept += b
        elif not nuevos:
            prio_acept = 0
    return traza



ALGORITMOS = [
    ("FCFS", lambda ps: fcfs(ps)),
    ("RR1 ", lambda ps: round_robin(ps, 1)),
    ("RR4 ", lambda ps: round_robin(ps, 4)),
    ("SPN ", lambda ps: spn(ps)),
    ("FB  ", lambda ps: fb(ps)),
    ("SRR ", lambda ps: srr(ps)),
]


def imprime_ronda(titulo, procs):
    print(f"- {titulo}:")
    print(f"  {resumen_procesos(procs)}")
    for nombre, fn in ALGORITMOS:
        traza = fn(procs)
        T, E, P = metricas(procs, traza)
        print(f"  {nombre.strip()}: T={T:.2f}, E={E:.2f}, P={P:.2f}")
        print(f"  {''.join(traza)}")



# La primera ronda siempre usa el ejemplo del enunciado
# Las siguientes cuatro rondas usan cargas aleatorias.

def main():
    if len(sys.argv) > 1:
        random.seed(int(sys.argv[1]))

    ejemplo = [
        {"nombre": "A", "llegada": 0,  "t": 3},
        {"nombre": "B", "llegada": 1,  "t": 5},
        {"nombre": "C", "llegada": 3,  "t": 2},
        {"nombre": "D", "llegada": 9,  "t": 5},
        {"nombre": "E", "llegada": 12, "t": 5},
    ]
    imprime_ronda("Ronda 1 (ejemplo del enunciado)",
                  ejemplo)
    print()

    etiquetas = ["Ronda 2", "Ronda 3", "Ronda 4", "Ronda 5"]
    for et in etiquetas:
        procs = genera_procesos(5)
        imprime_ronda(et, procs)
        print()


if __name__ == "__main__":
    main()