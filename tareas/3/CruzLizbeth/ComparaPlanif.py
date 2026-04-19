# Tarea 3
# El siguiente programa tiene como objetivo comparar los diferentes mecanismos de planificadores, van desde los mas sencillo FCFS
# RR(q=1 y q=4), SPN y FB (multinivel)
# Autora: Cruz Manriquez Lizbeth
# ************************************************************
# Importación de biblioteca
import random

# Para la simulación de los procesos, se define una función que los genere:

# Generar procesos

def generar_procesos():
    procesos = []
    for i in range(5):
        nombre = chr(65 + i)
        llegada = random.randint(0, 5)
        duracion = random.randint(1, 6)
        procesos.append([nombre, llegada, duracion])
    
    procesos.sort(key=lambda x: x[1])
    return procesos


# Para realizar la comparación entre los diferentes mecanismos pplanificadores
# se definen las métricas:

# Calcular métricas

def metricas(procesos, fin):
    T = 0 #Tiempo total desde que llega el proceso
    E = 0 #Tiempo de espera, donde el proceso permacene en cola
    P = 0 #Penalización, la relación entre tiempo total y tiempo de ejecución
    
    for p in procesos:
        nombre, llegada, duracion = p
        t_final = fin[nombre]
        
        t = t_final - llegada
        e = t - duracion
        p_ind = t / duracion
        
        T += t
        E += e
        P += p_ind
    
    n = len(procesos)
    return round(T/n,2), round(E/n,2), round(P/n,2)


# Primer mecanismo de planificación: First Come First Served
# Función FCFS

def fcfs(procesos):
    tiempo = 0
    linea = ""
    fin = {}

    for p in procesos:
        nombre, llegada, duracion = p
        
        if tiempo < llegada:
            tiempo = llegada
        
        for i in range(duracion):
            linea += nombre
            tiempo += 1
        
        fin[nombre] = tiempo
    
    return linea, metricas(procesos, fin)


# Segundo mecanismo, Round Robin (q=1 y q=4)
# Función Round Robin

def rr(procesos, q):
    tiempo = 0
    cola = []
    linea = ""
    fin = {}

    restantes = {p[0]: p[2] for p in procesos}

    i = 0
    while True:
        while i < len(procesos) and procesos[i][1] <= tiempo:
            cola.append(procesos[i][0])
            i += 1
        
        if len(cola) == 0:
            if i >= len(procesos):
                break
            tiempo += 1
            continue
        
        actual = cola.pop(0)
        ejec = min(q, restantes[actual])

        for j in range(ejec):
            linea += actual
            tiempo += 1

            while i < len(procesos) and procesos[i][1] <= tiempo:
                cola.append(procesos[i][0])
                i += 1
        
        restantes[actual] -= ejec

        if restantes[actual] > 0:
            cola.append(actual)
        else:
            fin[actual] = tiempo

    return linea, metricas(procesos, fin)


# Tercer mecanismo, Shortest Process Next
# Función SPN

def spn(procesos):
    tiempo = 0
    lista = []
    pendientes = procesos.copy()
    linea = ""
    fin = {}

    while len(pendientes) > 0 or len(lista) > 0:
        
        while len(pendientes) > 0 and pendientes[0][1] <= tiempo:
            lista.append(pendientes.pop(0))
        
        if len(lista) == 0:
            tiempo += 1
            continue
        
        lista.sort(key=lambda x: x[2])
        actual = lista.pop(0)

        nombre, llegada, duracion = actual

        for i in range(duracion):
            linea += nombre
            tiempo += 1
        
        fin[nombre] = tiempo

    return linea, metricas(procesos, fin)


# Se realiza un cuarto mecanismo Feedback Multinivel
# FB (multinivel simple)

def fb(procesos):
    tiempo = 0
    colas = [[], [], []]
    quantums = [1, 2, 4]

    linea = ""
    fin = {}
    restantes = {p[0]: p[2] for p in procesos}

    i = 0
    while True:
        while i < len(procesos) and procesos[i][1] <= tiempo:
            colas[0].append(procesos[i][0])
            i += 1
        
        nivel = -1
        for j in range(3):
            if len(colas[j]) > 0:
                nivel = j
                break
        
        if nivel == -1:
            if i >= len(procesos):
                break
            tiempo += 1
            continue
        
        actual = colas[nivel].pop(0)
        ejec = min(quantums[nivel], restantes[actual])

        for k in range(ejec):
            linea += actual
            tiempo += 1

            while i < len(procesos) and procesos[i][1] <= tiempo:
                colas[0].append(procesos[i][0])
                i += 1
        
        restantes[actual] -= ejec

        if restantes[actual] > 0:
            if nivel < 2:
                colas[nivel+1].append(actual)
            else:
                colas[nivel].append(actual)
        else:
            fin[actual] = tiempo

    return linea, metricas(procesos, fin)


# Función principal
# MAIN

for ronda in range(5):
    print("\n- Ronda", ronda+1)

    procesos = generar_procesos()

    # imprimir procesos y total
    total = 0
    linea_proc = ""
    for p in procesos:
        linea_proc += f"{p[0]}: {p[1]}, t={p[2]}; "
        total += p[2]

    print(" ", linea_proc.strip(), f"(tot:{total})")

    # FCFS
    l, m = fcfs(procesos)
    print(f"  FCFS: T={m[0]}, E={m[1]}, P={m[2]}")
    print("  ", l)

    # RR q=1
    l, m = rr(procesos, 1)
    print(f"  RR1: T={m[0]}, E={m[1]}, P={m[2]}")
    print("  ", l)

    # RR q=4
    l, m = rr(procesos, 4)
    print(f"  RR4: T={m[0]}, E={m[1]}, P={m[2]}")
    print("  ", l)

    # SPN
    l, m = spn(procesos)
    print(f"  SPN: T={m[0]}, E={m[1]}, P={m[2]}")
    print("  ", l)

    # FB
    l, m = fb(procesos)
    print(f"  FB: T={m[0]}, E={m[1]}, P={m[2]}")
    print("  ", l)
