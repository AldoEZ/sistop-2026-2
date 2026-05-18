

import random
from collections import deque


RONDAS = 5
PROCESOS_POR_RONDA = 5

# Genera una carga de procesos con tiempos de llegada y tiempos de CPU aleatorios.
# Luego compara FCFS, SPN, RR y FB con una vista simple de la ejecucion.
def generar_carga():
    carga = []
    llegada = 0
    for i in range(PROCESOS_POR_RONDA):
        if i > 0:
            llegada += random.randint(0, 3)
        tiempo_cpu = random.randint(2, 8)
        nombre = chr(ord("A") + i)
        carga.append((nombre, llegada, tiempo_cpu))
    return carga

# Muestra la carga en un formato legible.
def mostrar_carga(carga):
    partes = []
    total = 0
    for nombre, llegada, tiempo_cpu in carga:
        partes.append(f"{nombre}: {llegada}, cpu={tiempo_cpu}")
        total += tiempo_cpu
    print("; ".join(partes) + f"  (tot:{total})")

# Calcula el tiempo total, tiempo de espera y penalización.
def calcular_resultado(carga, fin, linea):
    t_total = 0
    e_total = 0
    p_total = 0
    n = len(carga)
    for nombre, llegada, tiempo_cpu in carga:
        t = fin[nombre] - llegada
        e = t - tiempo_cpu
        p = t / tiempo_cpu
        t_total += t
        e_total += e
        p_total += p
    return (t_total / n, e_total / n, p_total / n, "".join(linea))

# FCFS: ejecuta en el orden de llegada.
def fcfs(carga):
    tiempo = 0
    fin = {}
    linea = []
    for nombre, llegada, tiempo_cpu in carga:
        if tiempo < llegada:
            linea.extend("." for _ in range(llegada - tiempo))
            tiempo = llegada
        for _ in range(tiempo_cpu):
            linea.append(nombre)
            tiempo += 1
        fin[nombre] = tiempo
    return calcular_resultado(carga, fin, linea)

# SPN: elige el proceso con menor tiempo de CPU entre los listos.
def spn(carga):
    pendientes = carga[:]
    listos = []
    fin = {}
    linea = []
    tiempo = 0

    while pendientes or listos:
        for proceso in pendientes[:]:
            if proceso[1] <= tiempo:
                listos.append(proceso)
                pendientes.remove(proceso)

        if not listos:
            proxima = min(p[1] for p in pendientes)
            linea.extend("." for _ in range(proxima - tiempo))
            tiempo = proxima
            continue

        listos.sort(key=lambda x: (x[2], x[1]))
        nombre, _, tiempo_cpu = listos.pop(0)
        for _ in range(tiempo_cpu):
            linea.append(nombre)
            tiempo += 1
        fin[nombre] = tiempo

    return calcular_resultado(carga, fin, linea)

# RR: ejecuta cada proceso por un quantum fijo, luego lo reprograma al final de la cola.
def rr(carga, quantum):
    pendientes = carga[:]
    cola = deque()
    restantes = {}
    fin = {}
    linea = []
    tiempo = 0

    for nombre, llegada, tiempo_cpu in carga:
        restantes[nombre] = tiempo_cpu

    while pendientes or cola:
        for proceso in pendientes[:]:
            if proceso[1] <= tiempo:
                cola.append(proceso)
                pendientes.remove(proceso)

        if not cola:
            proxima = min(p[1] for p in pendientes)
            linea.extend("." for _ in range(proxima - tiempo))
            tiempo = proxima
            continue

        nombre, llegada, tiempo_cpu = cola.popleft()
        usado = min(quantum, restantes[nombre])
        for _ in range(usado):
            linea.append(nombre)
            tiempo += 1
            restantes[nombre] -= 1
            for proceso in pendientes[:]:
                if proceso[1] <= tiempo:
                    cola.append(proceso)
                    pendientes.remove(proceso)
        if restantes[nombre] > 0:
            cola.append((nombre, llegada, tiempo_cpu))
        else:
            fin[nombre] = tiempo

    return calcular_resultado(carga, fin, linea)

# FB: similar a RR pero con 3 niveles de quantum (1, 2, 4) y reprogramación a niveles inferiores.
def fb(carga):
    pendientes = carga[:]
    colas = [deque(), deque(), deque()]
    quanta = [1, 2, 4]
    restantes = {}
    fin = {}
    linea = []
    tiempo = 0

    for nombre, llegada, tiempo_cpu in carga:
        restantes[nombre] = tiempo_cpu

    while pendientes or colas[0] or colas[1] or colas[2]:
        for proceso in pendientes[:]:
            if proceso[1] <= tiempo:
                colas[0].append(proceso)
                pendientes.remove(proceso)

        nivel = 0
        while nivel < 3 and not colas[nivel]:
            nivel += 1

        if nivel == 3:
            proxima = min(p[1] for p in pendientes)
            linea.extend("." for _ in range(proxima - tiempo))
            tiempo = proxima
            continue

        nombre, llegada, tiempo_cpu = colas[nivel].popleft()
        usado = min(quanta[nivel], restantes[nombre])
        for _ in range(usado):
            linea.append(nombre)
            tiempo += 1
            restantes[nombre] -= 1
            for proceso in pendientes[:]:
                if proceso[1] <= tiempo:
                    colas[0].append(proceso)
                    pendientes.remove(proceso)

        if restantes[nombre] > 0:
            if nivel < 2:
                colas[nivel + 1].append((nombre, llegada, tiempo_cpu))
            else:
                colas[2].append((nombre, llegada, tiempo_cpu))
        else:
            fin[nombre] = tiempo

    return calcular_resultado(carga, fin, linea)

# Imprime los resultados de cada algoritmo de planificación.
def imprimir_algoritmo(nombre, resultado):
    t, e, p, linea = resultado
    print(f"  {nombre}: T={t:.2f}, E={e:.2f}, P={p:.2f}")
    print(f"  {linea}")

# Ejecuta una ronda completa de generación de carga y comparación de algoritmos.
def una_ronda(numero):
    carga = generar_carga()
    print(f"- Ronda {numero}:")
    mostrar_carga(carga)
    imprimir_algoritmo("FCFS", fcfs(carga))
    imprimir_algoritmo("RR1", rr(carga, 1))
    imprimir_algoritmo("RR4", rr(carga, 4))
    imprimir_algoritmo("SPN", spn(carga))
    imprimir_algoritmo("FB", fb(carga))


def main():
    print("Comparacion de planificadores")
    print()
    for i in range(1, RONDAS + 1):
        una_ronda(i)
        print()


if __name__ == "__main__":
    main()
