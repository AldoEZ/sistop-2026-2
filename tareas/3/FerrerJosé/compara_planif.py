import random
from collections import deque

NUM_RONDAS = 5
NUM_PROCESOS = 5
QUANTUMS = [1, 4]


def generar_carga(num_procesos=NUM_PROCESOS):
    procesos = []
    llegada_actual = 0

    for i in range(num_procesos):
        nombre = chr(ord('A') + i)

        if i == 0:
            llegada = 0
        else:
            llegada_actual += random.randint(0, 3)
            llegada = llegada_actual

        duracion = random.randint(2, 8)

        procesos.append({
            "id": nombre,
            "llegada": llegada,
            "duracion": duracion
        })

    return procesos


def copiar_procesos(procesos):
    copia = []
    for p in procesos:
        copia.append({
            "id": p["id"],
            "llegada": p["llegada"],
            "duracion": p["duracion"]
        })
    return copia


def calcular_metricas(procesos_originales, tiempos_finalizacion):
    t_total = 0
    e_total = 0
    p_total = 0

    for p in procesos_originales:
        turnaround = tiempos_finalizacion[p["id"]] - p["llegada"]
        espera = turnaround - p["duracion"]
        penalizacion = turnaround / p["duracion"]

        t_total += turnaround
        e_total += espera
        p_total += penalizacion

    n = len(procesos_originales)
    return (
        round(t_total / n, 2),
        round(e_total / n, 2),
        round(p_total / n, 2)
    )


def fcfs(procesos):
    procesos = sorted(copiar_procesos(procesos), key=lambda p: (p["llegada"], p["id"]))
    tiempo = 0
    timeline = []
    tiempos_finalizacion = {}

    for p in procesos:
        while tiempo < p["llegada"]:
            timeline.append("_")
            tiempo += 1

        for _ in range(p["duracion"]):
            timeline.append(p["id"])
            tiempo += 1

        tiempos_finalizacion[p["id"]] = tiempo

    return "".join(timeline), tiempos_finalizacion


def spn(procesos):
    procesos = copiar_procesos(procesos)
    tiempo = 0
    timeline = []
    tiempos_finalizacion = {}
    completados = 0
    n = len(procesos)

    while completados < n:
        disponibles = [
            p for p in procesos
            if p["id"] not in tiempos_finalizacion and p["llegada"] <= tiempo
        ]

        if not disponibles:
            timeline.append("_")
            tiempo += 1
            continue

        actual = min(disponibles, key=lambda p: (p["duracion"], p["llegada"], p["id"]))

        for _ in range(actual["duracion"]):
            timeline.append(actual["id"])
            tiempo += 1

        tiempos_finalizacion[actual["id"]] = tiempo
        completados += 1

    return "".join(timeline), tiempos_finalizacion


def round_robin(procesos, quantum):
    procesos = sorted(copiar_procesos(procesos), key=lambda p: (p["llegada"], p["id"]))
    tiempo = 0
    timeline = []
    tiempos_finalizacion = {}

    cola = deque()
    i = 0
    n = len(procesos)

    restantes = {}
    for p in procesos:
        restantes[p["id"]] = p["duracion"]

    while len(tiempos_finalizacion) < n:
        while i < n and procesos[i]["llegada"] <= tiempo:
            cola.append(procesos[i])
            i += 1

        if not cola:
            timeline.append("_")
            tiempo += 1
            continue

        actual = cola.popleft()
        ejecutar = min(quantum, restantes[actual["id"]])

        for _ in range(ejecutar):
            timeline.append(actual["id"])
            tiempo += 1
            restantes[actual["id"]] -= 1

            while i < n and procesos[i]["llegada"] <= tiempo:
                cola.append(procesos[i])
                i += 1

            if restantes[actual["id"]] == 0:
                tiempos_finalizacion[actual["id"]] = tiempo
                break

        if restantes[actual["id"]] > 0:
            cola.append(actual)

    return "".join(timeline), tiempos_finalizacion


def imprimir_carga(procesos):
    partes = []
    total = 0

    for p in procesos:
        partes.append(f'{p["id"]}: {p["llegada"]}, t={p["duracion"]}')
        total += p["duracion"]

    print("  " + "; ".join(partes))
    print(f"    (tot:{total})")


def ejecutar_ronda(procesos):
    print("- Carga:")
    imprimir_carga(procesos)

    timeline_fcfs, fin_fcfs = fcfs(procesos)
    t, e, p = calcular_metricas(procesos, fin_fcfs)
    print(f"  FCFS: T={t}, E={e}, P={p}")
    print(f"  {timeline_fcfs}")

    timeline_rr1, fin_rr1 = round_robin(procesos, 1)
    t, e, p = calcular_metricas(procesos, fin_rr1)
    print(f"  RR1:  T={t}, E={e}, P={p}")
    print(f"  {timeline_rr1}")

    timeline_rr4, fin_rr4 = round_robin(procesos, 4)
    t, e, p = calcular_metricas(procesos, fin_rr4)
    print(f"  RR4:  T={t}, E={e}, P={p}")
    print(f"  {timeline_rr4}")

    timeline_spn, fin_spn = spn(procesos)
    t, e, p = calcular_metricas(procesos, fin_spn)
    print(f"  SPN:  T={t}, E={e}, P={p}")
    print(f"  {timeline_spn}")


def main():
    random.seed()

    print("Comparación de algoritmos de planificación")
    print("=" * 45)

    for ronda in range(1, NUM_RONDAS + 1):
        print(f"\nRonda {ronda}:")
        procesos = generar_carga()
        ejecutar_ronda(procesos)


if __name__ == "__main__":
    main()