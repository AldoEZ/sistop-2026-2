import random

class Proceso:
    def __init__(self, nombre, llegada, rafaga):
        self.nombre = nombre            
        self.llegada = llegada          
        self.rafaga = rafaga            
        self.restante = rafaga          
        self.fin = 0                    
        self.inicio_ejecucion = -1      

    # Método que calcula los indicadores de rendimiento del proceso tras su finalizacion
    def metricas(self):
        t_respuesta = self.fin - self.llegada
        espera = t_respuesta - self.rafaga
        penalizacion = t_respuesta / self.rafaga
        return t_respuesta, espera, penalizacion

# Función que generará 5 cargas (procesos) con características distintas
def generar_carga(n=5):
    procesos = []
    tiempo_llegada = 0
    for i in range(n):
        nombre = chr(65 + i)
        rafaga = random.randint(2, 7)
        procesos.append(Proceso(nombre, tiempo_llegada, rafaga))
        tiempo_llegada += random.randint(0, 3)
    return procesos

# Función que imprime los resultados individuales de los procesos que ya terminaron
# Dibuja el esquema visual
def imprimir_resultados(nombre_alg, procesos, gantt):
    print(f"  {nombre_alg}:", end=" ")
    t_total, e_total, p_total = 0, 0, 0
    for p in procesos:
        t, e, p_val = p.metricas()
        t_total += t; e_total += e; p_total += p_val
    
    n = len(procesos)
    print(f"T={t_total/n:.2f}, E={e_total/n:.2f}, P={p_total/n:.2f}")
    print(f"      {''.join(gantt)}")  # Genera el esquema visual de ejecución


# Funciones de los mecanismos de planificación de procesos FCFS, RR, SPN y FB

# Algoritmo FCFS
def fcfs(carga):
    procesos = sorted([Proceso(p.nombre, p.llegada, p.rafaga) for p in carga], key=lambda x: x.llegada)
    tiempo, gantt = 0, []
    for p in procesos:
        if tiempo < p.llegada:
            gantt.extend(['-'] * (p.llegada - tiempo))
            tiempo = p.llegada
        for _ in range(p.rafaga):
            gantt.append(p.nombre)
            tiempo += 1
        p.fin = tiempo
        
    # Impresion de resultados
    imprimir_resultados("FCFS", procesos, gantt)

# Algoritmo RR
def rr(carga, q):
    procesos = [Proceso(p.nombre, p.llegada, p.rafaga) for p in carga]
    tiempo, gantt, cola = 0, [], []
    terminados = []
    
    while len(terminados) < len(procesos):
        # Si un proceso llega, se forma al final de la cola de procesos
        for p in procesos:
            if p.llegada <= tiempo and p not in cola and p not in terminados:
                cola.append(p)
        
        if not cola:
            gantt.append('-')
            tiempo += 1
            continue
            
        # Toma el proceso al frente de la cola (FIFO)
        curr = cola.pop(0)
        ejecutar = min(curr.restante, q)
        for _ in range(ejecutar):
            gantt.append(curr.nombre)
            tiempo += 1
            # Se revisa si hay llegadas de procesos durante el quantum
            for p in procesos:
                if p.llegada == tiempo and p not in cola and p not in terminados:
                    cola.append(p)
        
        curr.restante -= ejecutar
        if curr.restante == 0:
            # El proceso termina su trabajo
            curr.fin = tiempo
            terminados.append(curr)
        else:
            cola.append(curr)
            
    # Impresion de resultados
    imprimir_resultados(f"RR{q}", procesos, gantt)

def spn(carga):
    procesos = [Proceso(p.nombre, p.llegada, p.rafaga) for p in carga]
    tiempo, gantt, terminados = 0, [], []
    
    while len(terminados) < len(procesos):
        # Filtramos procesos que ya llegaron y no han finalizado
        disponibles = [p for p in procesos if p.llegada <= tiempo and p not in terminados]
        if not disponibles:
            gantt.append('-')
            tiempo += 1
            continue
        
        # Se selecciona el proceso con la ráfaga más corta
        proximo = min(disponibles, key=lambda x: x.rafaga)
        
        # El proceso se ejecuta hasta terminar
        for _ in range(proximo.rafaga):
            gantt.append(proximo.nombre)
            tiempo += 1
            
        proximo.fin = tiempo 
        terminados.append(proximo)

    # Impresion de resultados
    imprimir_resultados("SPN", procesos, gantt)

def fb(carga):
    # Se genera una copia de la carga para no afectar los datos originales
    procesos = [Proceso(p.nombre, p.llegada, p.rafaga) for p in carga]
    tiempo, gantt = 0, []
    
    # Se crean 5 colas de procesos listos, cada una con un nivel de prioridad distinto
    colas = [[] for _ in range(5)]
    terminados = []
    
    # Ciclo que se detiene solo hasta que todos los procesos alcancen el estado Terminado
    while len(terminados) < len(procesos):
        
        # Aquí los procesos recién llegados entran a la cola de mayor prioridad
        for p in procesos:
            if p.llegada == tiempo:
                colas[0].append((p, 0)) 
        
        # Se busca el proceso al frente de la cola de más prioridad disponible
        curr_p, nivel = None, -1
        for i in range(5):
            if colas[i]:
                curr_p, nivel = colas[i].pop(0)
                break
        
        if curr_p:
            gantt.append(curr_p.nombre)
            tiempo += 1
            curr_p.restante -= 1
            if curr_p.restante == 0:
                curr_p.fin = tiempo
                terminados.append(curr_p)
            else:
                nuevo_nivel = min(nivel + 1, 4) 
                colas[nuevo_nivel].append((curr_p, nuevo_nivel))
        else:
            gantt.append('-')
            tiempo += 1
            
    # Impresion de resultados
    imprimir_resultados("FB", procesos, gantt)


# Ejecución principal del programa
 
for i in range(1, 6):
    print(f"- Ronda {i}:")
    carga = generar_carga()
    desc = "; ".join([f"{p.nombre}: {p.llegada}, t={p.rafaga}" for p in carga])
    print(f"    {desc}")
    fcfs(carga)
    rr(carga, 1)
    rr(carga, 4)
    spn(carga)
    fb(carga)
    print()
    