import random
from collections import deque


# Genera 5 procesos con llegada y duración aleatoria
def generar_procesos(n=5):
    procesos = []
    tiempo_actual = 0

    for i in range(n):
        llegada = tiempo_actual + random.randint(0, 3)
        duracion = random.randint(2, 6)

        procesos.append({
            "id": chr(65 + i),
            "llegada": llegada,
            "duracion": duracion
        })

        tiempo_actual = llegada

    return procesos


# Calcula T (turnaround), E (espera) y P (penalización)
def calcular_metricas(resultados):
    T = []
    E = []
    P = []

    for r in resultados:
        t = r["fin"] - r["llegada"]
        e = t - r["duracion"]
        p = t / r["duracion"]

        T.append(t)
        E.append(e)
        P.append(p)

    return round(sum(T)/len(T), 2), round(sum(E)/len(E), 2), round(sum(P)/len(P), 2)


# FCFS: ejecuta en orden de llegada
def fcfs(procesos):
    tiempo = 0
    timeline = ""
    resultados = []

    for p in procesos:
        if tiempo < p["llegada"]:
            tiempo = p["llegada"]

        timeline += p["id"] * p["duracion"]
        tiempo += p["duracion"]

        resultados.append({
            **p,
            "fin": tiempo
        })

    return timeline, resultados


# SPN: ejecuta primero el proceso más corto disponible
def spn(procesos):
    tiempo = 0
    timeline = ""
    pendientes = procesos[:]
    listos = []
    resultados = []

    while pendientes or listos:
        listos += [p for p in pendientes if p["llegada"] <= tiempo]
        pendientes = [p for p in pendientes if p["llegada"] > tiempo]

        if not listos:
            tiempo += 1
            continue

        listos.sort(key=lambda x: x["duracion"])
        p = listos.pop(0)

        timeline += p["id"] * p["duracion"]
        tiempo += p["duracion"]

        resultados.append({
            **p,
            "fin": tiempo
        })

    return timeline, resultados


# Round Robin con quantum variable
def rr(procesos, quantum):
    tiempo = 0
    cola = deque()
    pendientes = procesos[:]
    timeline = ""
    restantes = {p["id"]: p["duracion"] for p in procesos}
    resultados = {}

    while pendientes or cola:
        cola.extend([p for p in pendientes if p["llegada"] <= tiempo])
        pendientes = [p for p in pendientes if p["llegada"] > tiempo]

        if not cola:
            tiempo += 1
            continue

        p = cola.popleft()
        ejecucion = min(quantum, restantes[p["id"]])

        timeline += p["id"] * ejecucion
        restantes[p["id"]] -= ejecucion
        tiempo += ejecucion

        cola.extend([x for x in pendientes if x["llegada"] <= tiempo])
        pendientes = [x for x in pendientes if x["llegada"] > tiempo]

        if restantes[p["id"]] > 0:
            cola.append(p)
        else:
            resultados[p["id"]] = {
                **p,
                "fin": tiempo
            }

    return timeline, list(resultados.values())


# FB: colas multinivel con quantums 1, 2 y 4
def fb(procesos):
    tiempo = 0
    colas = [deque(), deque(), deque()]
    quantums = [1, 2, 4]

    pendientes = procesos[:]
    restantes = {p["id"]: p["duracion"] for p in procesos}
    resultados = {}
    timeline = ""

    while pendientes or any(colas):
        # nuevos procesos entran al nivel más alto
        for p in pendientes[:]:
            if p["llegada"] <= tiempo:
                colas[0].append(p)
                pendientes.remove(p)

        ejecutado = False

        # revisar cada cola por prioridad
        for nivel in range(3):
            if colas[nivel]:
                p = colas[nivel].popleft()
                q = min(quantums[nivel], restantes[p["id"]])

                timeline += p["id"] * q
                restantes[p["id"]] -= q
                tiempo += q

                # revisar si llegaron nuevos procesos
                for x in pendientes[:]:
                    if x["llegada"] <= tiempo:
                        colas[0].append(x)
                        pendientes.remove(x)

                if restantes[p["id"]] > 0:
                    if nivel < 2:
                        colas[nivel+1].append(p)
                    else:
                        colas[nivel].append(p)
                else:
                    resultados[p["id"]] = {
                        **p,
                        "fin": tiempo
                    }

                ejecutado = True
                break

        if not ejecutado:
            tiempo += 1

    return timeline, list(resultados.values())


# imprime los procesos generados en la ronda
def imprimir_procesos(procesos):
    total = sum(p["duracion"] for p in procesos)

    for p in procesos:
        print(f"{p['id']}: llegada={p['llegada']} duracion={p['duracion']}")

    print(f"(total: {total})")


# imprime métricas de cada algoritmo
def imprimir_resultado(nombre, timeline, resultados):
    T, E, P = calcular_metricas(resultados)
    print(f"\n{nombre}: T={T}, E={E}, P={P}")
    print(timeline)


# ejecuta 5 rondas con todos los algoritmos
def ejecutar():
    for ronda in range(5):
        print(f"\n--- Ronda {ronda + 1} ---")

        procesos = generar_procesos()
        imprimir_procesos(procesos)

        tl, res = fcfs(procesos)
        imprimir_resultado("FCFS", tl, res)

        tl, res = rr(procesos, 1)
        imprimir_resultado("RR1", tl, res)

        tl, res = rr(procesos, 4)
        imprimir_resultado("RR4", tl, res)

        tl, res = spn(procesos)
        imprimir_resultado("SPN", tl, res)

        tl, res = fb(procesos)
        imprimir_resultado("FB", tl, res)


if __name__ == "__main__":
    ejecutar()
