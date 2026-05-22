import random
from collections import deque

# ================= GENERAR PROCESOS =================
# Aqui se le asigna un n=5 para que se pueda correr 5 veces y se utiliza la librería random para generar los procesos
def generar_procesos(n=5):
    procesos = []
    for i in range(n):
        llegada = random.randint(0, 10)
        duracion = random.randint(1, 7)
        procesos.append({
            "id": chr(65+i),
            "llegada": llegada,
            "duracion": duracion
        })
    return sorted(procesos, key=lambda x: x["llegada"]) #Se ordena el orden de llegada porque los algoritmos FCFS y SPN lo necesitan para no arrojar resultados incorrectos


# ================= FCFS =================
def fcfs(procesos):
    tiempo = 0
    resultado = []
    salida = ""

    for p in procesos: # si el proceso aún no llega, el CPU espera
        if tiempo < p["llegada"]:
            tiempo = p["llegada"]

        inicio = tiempo
        fin = inicio + p["duracion"]

        espera = inicio - p["llegada"]
        retorno = fin - p["llegada"]

        salida += p["id"] * p["duracion"]

        resultado.append((espera, retorno, p["duracion"])) #Se agrega a una lista para mostrarla en el formato especificado
        tiempo = fin

    return resultado, salida


# ================= ROUND ROBIN =================
def round_robin(procesos, tiempo_proceso):
    tiempo = 0
    cola = deque()
    procesos_restantes = {p["id"]: p["duracion"] for p in procesos}

    salida = ""
    completados = set()

    while len(completados) < len(procesos):
        for p in procesos:
            if p["llegada"] == tiempo:
                cola.append(p["id"])

        if cola:
            actual = cola.popleft()
            ejec = min(tiempo_proceso, procesos_restantes[actual])

            for _ in range(ejec):
                salida += actual
                tiempo += 1

                for p in procesos:
                    if p["llegada"] == tiempo:
                        cola.append(p["id"])

            procesos_restantes[actual] -= ejec #Actualiza los tiempos restantes

            if procesos_restantes[actual] > 0:
                cola.append(actual)
            else:
                completados.add(actual)
        else:
            tiempo += 1

    return salida


# ================= SPN =================
#Se elige el proceso más corto de los que lleguen
def spn(procesos):
    tiempo = 0
    pendientes = procesos[:]
    salida = "" #Siempre nuestra salida va a ser el orden el que se piden como AABCBACBC etc.

    while pendientes:
        disponibles = [p for p in pendientes if p["llegada"] <= tiempo]

        if not disponibles:
            tiempo += 1
            continue

        actual = min(disponibles, key=lambda x: x["duracion"]) #Se elige el proceso mas corto

        for _ in range(actual["duracion"]):
            salida += actual["id"]

        tiempo += actual["duracion"]
        pendientes.remove(actual)

    return salida


# ================= MÉTRICAS =================
def calcular_metricas(resultados):
    T = sum(r[1] for r in resultados) / len(resultados)
    E = sum(r[0] for r in resultados) / len(resultados)
    P = sum(r[1] / r[2] for r in resultados) / len(resultados)
    return T, E, P


def metricas_desde_timeline(salida, procesos): #Cada letra representa una unidad de tiempo, por lo que se recorre la salida para ver cuando termina cada proceso
    fin_procesos = {}

    for i, p in enumerate(salida):
        fin_procesos[p] = i + 1

    resultados = []

    for p in procesos:
        fin = fin_procesos[p["id"]]
        retorno = fin - p["llegada"]
        espera = retorno - p["duracion"]

        resultados.append((espera, retorno, p["duracion"]))

    return resultados


if __name__ == "__main__":
    rondas = 5 #Minimo se puso 5 rondas para mejor visualizacion 

    for r in range(rondas):
        print(f"\n================ RONDA {r+1} ================")

        procesos = generar_procesos()

        print("Procesos:")
        for p in procesos:
            print(f"{p['id']}: llegada={p['llegada']}, t={p['duracion']}", end="; ")
        print("\n")
        
        res_fcfs, tl_fcfs = fcfs(procesos)
        T, E, P = calcular_metricas(res_fcfs)
        print(f"FCFS: T={T:.2f}, E={E:.2f}, P={P:.2f}")
        print(tl_fcfs)
        print()

        tl_rr1 = round_robin(procesos, 1)
        res_rr1 = metricas_desde_timeline(tl_rr1, procesos)
        T, E, P = calcular_metricas(res_rr1)
        print(f"RR1: T={T:.2f}, E={E:.2f}, P={P:.2f}")
        print(tl_rr1)
        print()
        
        tl_rr4 = round_robin(procesos, 4)
        res_rr4 = metricas_desde_timeline(tl_rr4, procesos)
        T, E, P = calcular_metricas(res_rr4)
        print(f"RR4: T={T:.2f}, E={E:.2f}, P={P:.2f}")
        print(tl_rr4)
        print()

        tl_spn = spn(procesos)
        res_spn = metricas_desde_timeline(tl_spn, procesos)
        T, E, P = calcular_metricas(res_spn)
        print(f"SPN: T={T:.2f}, E={E:.2f}, P={P:.2f}")
        print(tl_spn)
        print()
