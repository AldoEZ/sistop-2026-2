#!/usr/bin/env python3

import random
import string

# ========================= CONFIGURACION GENERAL =========================

NUM_PROCESOS = 6
RANGO_TIEMPO = (1, 10)
RANGO_LLEGADA = (1, 15)

# --------------------- Configuracion FB (Retroalimentacion) --------------
NUM_FILAS = 4
QUANTUM_BASE = 1
MAX_EJECUCIONES = 2

# --------------------- Configuracion SRR (Selfish Round Robin) ----------
QUANTUM_SRR = 2
INCREMENTO_A = 2
INCREMENTO_B = 1

# --------------------- Configuracion RR (Round Robin) -------------------
QUANTUMS_RR = [1, 4]          # se usaran dos opciones distintas

# ========================= FUNCIONES AUXILIARES COMUNES ==================

def obtenerLlegada(proceso):
    return proceso["tiempoLlegada"]

def obtenerPID(proceso):
    return proceso["PID"]

def obtenerTiempoCorto(proceso):
    return (proceso["tiempo"], proceso["tiempoLlegada"], proceso["PID"])

# --------------------- METRICAS -----------------------------------------

def obtenerTiempoTotal(proceso):
    return proceso["tiempoFinal"] - proceso["tiempoLlegada"]

def obtenerEspera(proceso):
    return obtenerTiempoTotal(proceso) - proceso["tiempo"]

def obtenerPenalty(proceso):
    return obtenerTiempoTotal(proceso) / proceso["tiempo"]

# --------------------- GENERADORES DE PROCESOS (cada algoritmo usa el suyo) --

def generarProcesos_FB(n):
    """Genera procesos con los campos que necesita el planificador FB."""
    letras = list(string.ascii_uppercase[:n])
    random.shuffle(letras)
    procesos = []
    for i in range(n):
        t = random.randint(RANGO_TIEMPO[0], RANGO_TIEMPO[1])
        proceso = {
            "PID": letras[i],
            "tiempo": t,
            "tiempoLlegada": random.randint(RANGO_LLEGADA[0], RANGO_LLEGADA[1]),
            "tiempoRestante": t,
            "filaActual": 0,
            "ejecuciones": 0,
            "tiempoFinal": 0,
            "tiempoEspera": 0,
            "tiempoInicio": -1,
            "iniciado": False
        }
        procesos.append(proceso)

    procesos.sort(key=obtenerLlegada)

    # normalizar tiempo de llegada para que el primero empiece en 0
    minLlegada = procesos[0]["tiempoLlegada"]
    for p in procesos:
        p["tiempoLlegada"] -= minLlegada

    return procesos

def generarProcesos_SRR(n):
    """Genera procesos con los campos que necesita el planificador SRR."""
    letras = list(string.ascii_uppercase[:n])
    random.shuffle(letras)
    procesos = []
    for i in range(n):
        t = random.randint(RANGO_TIEMPO[0], RANGO_TIEMPO[1])
        proceso = {
            "PID": letras[i],
            "tiempo": t,
            "tiempoLlegada": random.randint(RANGO_LLEGADA[0], RANGO_LLEGADA[1]),
            "tiempoRestante": t,
            "prioridad": 0,
            "tiempoFinal": 0,
            "tiempoEspera": 0,
            "tiempoInicio": -1,
            "iniciado": False
        }
        procesos.append(proceso)

    procesos.sort(key=obtenerLlegada)

    minLlegada = procesos[0]["tiempoLlegada"]
    for p in procesos:
        p["tiempoLlegada"] -= minLlegada

    return procesos

def generarProcesos_Mec(n):
    """Genera procesos basicos para FCFS, RR y SPN (con shuffle y rangos unificados)."""
    letras = list(string.ascii_uppercase[:n])
    random.shuffle(letras)
    procesos = []
    for i in range(n):
        t = random.randint(RANGO_TIEMPO[0], RANGO_TIEMPO[1])
        llegada = random.randint(RANGO_LLEGADA[0], RANGO_LLEGADA[1])
        proceso = {
            "PID": letras[i],
            "tiempo": t,
            "tiempoLlegada": llegada,
            "tiempoRestante": t,
            "tiempoFinal": 0,
            "tiempoInicio": -1,
            "iniciado": False,
        }
        procesos.append(proceso)

    procesos.sort(key=obtenerLlegada)

    minLlegada = procesos[0]["tiempoLlegada"]
    for p in procesos:
        p["tiempoLlegada"] -= minLlegada

    return procesos

def copiarProcesos(procesos):
    """Copia una lista de procesos (solo los campos comunes)."""
    copia = []
    for p in procesos:
        copia.append({
            "PID": p["PID"],
            "tiempo": p["tiempo"],
            "tiempoLlegada": p["tiempoLlegada"],
            "tiempoRestante": p["tiempoRestante"],
            "tiempoFinal": p["tiempoFinal"],
            "tiempoInicio": p["tiempoInicio"],
            "iniciado": p["iniciado"],
            # campos adicionales (si existen) se copian tambien
            "filaActual": p.get("filaActual", 0),
            "ejecuciones": p.get("ejecuciones", 0),
            "tiempoEspera": p.get("tiempoEspera", 0),
            "prioridad": p.get("prioridad", 0),
        })
    return copia

# ========================= IMPRESION ===================

def imprimirLineaTiempo(lineaTiempo):
    print("\n---Linea de Tiempo---")
    print("".join(lineaTiempo))

def imprimirMetricas(completados):
    print("\n---Metricas por proceso----------------------------")
    print(f"{'PID':<6} {'Inicio':>4} {'Fin':>4} {'T':>4} {'E':>4} {'P':>6}")
    print("-" * 42)

    totalT = 0
    totalE = 0
    totalP = 0

    for p in completados:
        T = obtenerTiempoTotal(p)
        E = obtenerEspera(p)
        P = obtenerPenalty(p)

        totalT += T
        totalE += E
        totalP += P

        print(f"{p['PID']:<6} {p['tiempoInicio']:>4} {p['tiempoFinal']:>4} {T:>4} {E:>4} {P:>6.2f}")

    n = len(completados)
    print("-" * 42)
    print(f"{'PROM':<6} {'':>4} {'':>4} {totalT/n:>4.1f} {totalE/n:>4.1f} {totalP/n:>6.2f}")

def imprimirParamsProcesos(procesos):
    print("\n---Procesos Generados---")
    print(f"{'PID':<6} {'Tiempo':>6} {'Llegada':>8}")
    print("-" * 24)
    for p in procesos:
        print(f"{p['PID']:<6} {p['tiempo']:>6} {p['tiempoLlegada']:>8}")

# ========================= PLANIFICADORES ===============================

# --------------------- FCFS -------------------
def planificadorFCFS(procesos):
    pendientes = sorted(procesos, key=obtenerLlegada)
    completados = []
    lineaTiempo = []
    tiempoActual = 0

    for p in pendientes:
        while tiempoActual < p["tiempoLlegada"]:
            lineaTiempo.append("_")
            tiempoActual += 1

        if not p["iniciado"]:
            p["tiempoInicio"] = tiempoActual
            p["iniciado"] = True

        for i in range(p["tiempo"]):
            lineaTiempo.append(p["PID"])
            tiempoActual += 1

        p["tiempoRestante"] = 0
        p["tiempoFinal"] = tiempoActual
        completados.append(p)

    return completados, lineaTiempo

# --------------------- Round Robin ------------
def planificadorRR(procesos, quantum):
    pendientes = sorted(procesos, key=obtenerLlegada)
    listos = []
    completados = []
    lineaTiempo = []
    tiempoActual = 0
    idx = 0
    total = len(pendientes)

    while len(completados) < total:
        while idx < total and pendientes[idx]["tiempoLlegada"] <= tiempoActual:
            listos.append(pendientes[idx])
            idx += 1

        if len(listos) == 0:
            lineaTiempo.append("_")
            tiempoActual += 1
            continue

        actual = listos.pop(0)

        if not actual["iniciado"]:
            actual["tiempoInicio"] = tiempoActual
            actual["iniciado"] = True

        rebanada = min(quantum, actual["tiempoRestante"])

        for i in range(rebanada):
            lineaTiempo.append(actual["PID"])
            tiempoActual += 1
            actual["tiempoRestante"] -= 1

            while idx < total and pendientes[idx]["tiempoLlegada"] <= tiempoActual:
                listos.append(pendientes[idx])
                idx += 1

            if actual["tiempoRestante"] == 0:
                break

        if actual["tiempoRestante"] == 0:
            actual["tiempoFinal"] = tiempoActual
            completados.append(actual)
        else:
            listos.append(actual)

    return completados, lineaTiempo

# --------------------- SPN (Shortest Process Next) ----------------------
def planificadorSPN(procesos):
    pendientes = sorted(procesos, key=obtenerLlegada)
    listos = []
    completados = []
    lineaTiempo = []
    tiempoActual = 0
    idx = 0
    total = len(pendientes)

    while len(completados) < total:
        while idx < total and pendientes[idx]["tiempoLlegada"] <= tiempoActual:
            listos.append(pendientes[idx])
            idx += 1

        if len(listos) == 0:
            lineaTiempo.append("_")
            tiempoActual += 1
            continue

        listos.sort(key=obtenerTiempoCorto)
        actual = listos.pop(0)

        if not actual["iniciado"]:
            actual["tiempoInicio"] = tiempoActual
            actual["iniciado"] = True

        while actual["tiempoRestante"] > 0:
            lineaTiempo.append(actual["PID"])
            tiempoActual += 1
            actual["tiempoRestante"] -= 1

            while idx < total and pendientes[idx]["tiempoLlegada"] <= tiempoActual:
                listos.append(pendientes[idx])
                idx += 1

        actual["tiempoFinal"] = tiempoActual
        completados.append(actual)

    return completados, lineaTiempo

# --------------------- FB (Retroalimentacion multinivel) ----------------
def planificadorFB(filaLlegada):
    filas = []
    for i in range(NUM_FILAS):
        filas.append([])

    completados = []
    lineaTiempo = []

    tiempoActual = 0

    while True:
        algoEnFila = len(filaLlegada) > 0

        if not algoEnFila:
            for f in filas:
                if len(f) > 0:
                    algoEnFila = True
                    break

        if not algoEnFila:
            break

        # mover llegados a fila 0
        for p in filaLlegada.copy():
            if p["tiempoLlegada"] <= tiempoActual:
                filas[0].append(p)
                filaLlegada.remove(p)

        # elegir siguiente proceso de la fila no vacia mas alta
        procesoActual = None
        for f in filas:
            if len(f) > 0:
                procesoActual = f.pop(0)
                break

        if procesoActual is None:
            tiempoActual += 1
            continue

        if not procesoActual["iniciado"]:
            procesoActual["tiempoInicio"] = tiempoActual
            procesoActual["iniciado"] = True

        nivel = procesoActual["filaActual"]
        quantum = QUANTUM_BASE * (2 ** nivel)
        tiempoEjecucion = min(quantum, procesoActual["tiempoRestante"])

        inicioTick = tiempoActual
        tiempoActual += tiempoEjecucion
        procesoActual["tiempoRestante"] -= tiempoEjecucion
        procesoActual["ejecuciones"] += 1

        for i in range(tiempoEjecucion):
            lineaTiempo.append(procesoActual["PID"])

        for f in filas:
            for p in f:
                p["tiempoEspera"] += tiempoEjecucion

        # revisar nuevos procesos llegados durante este tiempo
        for p in filaLlegada.copy():
            if p["tiempoLlegada"] <= tiempoActual:
                filas[0].append(p)
                filaLlegada.remove(p)

        if procesoActual["tiempoRestante"] == 0:
            procesoActual["tiempoFinal"] = tiempoActual
            completados.append(procesoActual)
        elif procesoActual["ejecuciones"] >= MAX_EJECUCIONES and nivel < NUM_FILAS - 1:
            procesoActual["filaActual"] += 1
            procesoActual["ejecuciones"] = 0
            filas[procesoActual["filaActual"]].append(procesoActual)
        else:
            filas[nivel].append(procesoActual)

    return completados, lineaTiempo

# --------------------- SRR (Selfish Round Robin) ------------------------
def planificadorSRR(filaLlegada):
    aceptados = []
    nuevos = []
    minPrioridadAcept = 0
    completados = []
    lineaTiempo = []

    tiempoActual = 0

    while True:
        algoEnFila = len(filaLlegada) > 0

        if not algoEnFila:
            if len(aceptados) > 0 or len(nuevos) > 0:
                algoEnFila = True

        if not algoEnFila:
            break

        # mover llegados a nuevos
        for p in filaLlegada.copy():
            if p["tiempoLlegada"] <= tiempoActual:
                nuevos.append(p)
                filaLlegada.remove(p)

        # comparar prioridad entre aceptados y nuevos
        if len(aceptados) > 0:
            minPrioridadAcept = aceptados[0]["prioridad"]
            for p in aceptados:
                if p["prioridad"] < minPrioridadAcept:
                    minPrioridadAcept = p["prioridad"]

        for p in nuevos.copy():
            if p["prioridad"] >= minPrioridadAcept:
                aceptados.append(p)
                nuevos.remove(p)

        if len(aceptados) == 0:
            for p in nuevos.copy():
                aceptados.append(p)
                nuevos.remove(p)

        if len(aceptados) == 0:
            tiempoActual += 1
            continue

        procesoActual = aceptados.pop(0)

        if procesoActual is None:
            tiempoActual += 1
            continue

        if not procesoActual["iniciado"]:
            procesoActual["tiempoInicio"] = tiempoActual
            procesoActual["iniciado"] = True

        tiempoEjecucion = min(QUANTUM_SRR, procesoActual["tiempoRestante"])

        inicioTick = tiempoActual
        tiempoActual += tiempoEjecucion
        procesoActual["tiempoRestante"] -= tiempoEjecucion

        for i in range(tiempoEjecucion):
            lineaTiempo.append(procesoActual["PID"])

        for p in aceptados:
            p["prioridad"] += INCREMENTO_A
        for p in nuevos:
            p["prioridad"] += INCREMENTO_B

        for p in aceptados:
            p["tiempoEspera"] += tiempoEjecucion
        for p in nuevos:
            p["tiempoEspera"] += tiempoEjecucion

        # revisar nuevos procesos llegados durante este tiempo
        for p in filaLlegada.copy():
            if p["tiempoLlegada"] <= tiempoActual:
                nuevos.append(p)
                filaLlegada.remove(p)

        if procesoActual["tiempoRestante"] == 0:
            procesoActual["tiempoFinal"] = tiempoActual
            completados.append(procesoActual)
        else:
            aceptados.append(procesoActual)

    return completados, lineaTiempo

# ========================= MENU PRINCIPAL ===============================

def main():
    while True:
        print("\n" + "=" * 50)
        print("     ALGORITMOS DE PLANIFICACION DE PROCESOS")
        print("=" * 50)
        print("1. FCFS (First Come First Served)")
        print("2. Round Robin (Quantum = 1)")
        print("3. Round Robin (Quantum = 4)")
        print("4. SPN (Shortest Process Next)")
        print("5. FB (Retroalimentacion multinivel)")
        print("6. SRR (Selfish Round Robin)")
        print("0. Salir")
        print("-" * 50)

        opcion = input("Seleccione una opcion: ").strip()

        if opcion == "0":
            print("Saliendo...")
            break
        elif opcion == "1":
            print("\n--- Ejecutando FCFS ---")
            procesos = generarProcesos_Mec(NUM_PROCESOS)
            imprimirParamsProcesos(procesos)
            completados, linea = planificadorFCFS(copiarProcesos(procesos))
            imprimirLineaTiempo(linea)
            imprimirMetricas(completados)
        elif opcion == "2":
            print("\n--- Ejecutando Round Robin (Quantum = 1) ---")
            procesos = generarProcesos_Mec(NUM_PROCESOS)
            imprimirParamsProcesos(procesos)
            completados, linea = planificadorRR(copiarProcesos(procesos), 1)
            imprimirLineaTiempo(linea)
            imprimirMetricas(completados)
        elif opcion == "3":
            print("\n--- Ejecutando Round Robin (Quantum = 4) ---")
            procesos = generarProcesos_Mec(NUM_PROCESOS)
            imprimirParamsProcesos(procesos)
            completados, linea = planificadorRR(copiarProcesos(procesos), 4)
            imprimirLineaTiempo(linea)
            imprimirMetricas(completados)
        elif opcion == "4":
            print("\n--- Ejecutando SPN ---")
            procesos = generarProcesos_Mec(NUM_PROCESOS)
            imprimirParamsProcesos(procesos)
            completados, linea = planificadorSPN(copiarProcesos(procesos))
            imprimirLineaTiempo(linea)
            imprimirMetricas(completados)
        elif opcion == "5":
            print("\n--- Ejecutando FB (Retroalimentacion multinivel) ---")
            print(f"Filas: {NUM_FILAS} | Quantum Base: {QUANTUM_BASE} | Max ejecuciones: {MAX_EJECUCIONES}")
            print("Quantum por nivel: ", end="")
            for i in range(NUM_FILAS):
                print(f"Q{i}={QUANTUM_BASE * (2 ** i)}", end=" ")
            print()
            procesos = generarProcesos_FB(NUM_PROCESOS)
            imprimirParamsProcesos(procesos)
            completados, linea = planificadorFB(copiarProcesos(procesos))
            imprimirLineaTiempo(linea)
            imprimirMetricas(completados)
        elif opcion == "6":
            print("\n--- Ejecutando SRR (Selfish Round Robin) ---")
            print(f"Quantum: {QUANTUM_SRR} | Incremento Aceptados: {INCREMENTO_A} | Incremento Nuevos: {INCREMENTO_B}")
            procesos = generarProcesos_SRR(NUM_PROCESOS)
            imprimirParamsProcesos(procesos)
            completados, linea = planificadorSRR(copiarProcesos(procesos))
            imprimirLineaTiempo(linea)
            imprimirMetricas(completados)
        else:
            print("Opcion no valida. Intente de nuevo.")

main()
