import random #libreria para sacar numeros al azar

#para crear los objetos de cada proceso
class Proceso: 
    def __init__(self, nombre, llegada, tiempo):
        self.nombre = nombre #guardamos la letra del proceso
        self.llegada = llegada #el segundo en el que llega el proceso
        self.tiempo = tiempo #cuanto tiempo necesita para acabar
        self.restante = tiempo #tiempo que le falta (se usa en rr y fb)
        self.final = 0 #guardamos cuando termine todo
        self.inicio_ejecucion = -1 #guarda cuando toco el cpu por primera vez

#para calcular los promedios de t, e y p
def calcular_metricas(lista):
    t_total, e_total, p_total = 0, 0, 0 #ontadores en cero
    n = len(lista) #total de procesos
    for p in lista:
        t = p.final - p.llegada #tiempo de retorno
        e = t - p.tiempo #tiempo que estuvo esperando
        p_val = t / p.tiempo #penalizacion del proceso
        t_total += t
        e_total += e
        p_total += p_val
    #regresamos los promedios redondeados a dos numeritos
    return round(t_total/n, 2), round(e_total/n, 2), round(p_total/n, 2)

#algoritmo fcfs: el primero que llega es el primero que se atiende
def fcfs(procesos_orig):
    #creamos copias de los procesos para no mover los originales
    lista = [Proceso(p.nombre, p.llegada, p.tiempo) for p in procesos_orig]
    lista.sort(key=lambda x: x.llegada) #los ordenamos por orden de llegada
    tiempo, gantt = 0, "" #empezamos el reloj y la cadena visual
    for p in lista:
        if tiempo < p.llegada: tiempo = p.llegada #si no ha llegado nadie el reloj avanza
        for _ in range(p.tiempo): #el proceso ocupa el cpu todo su tiempo
            gantt += p.nombre #pegamos la letra del proceso
            tiempo += 1
        p.final = tiempo
    t, e, p_met = calcular_metricas(lista) #sacamos los promedios
    return f"FCFS: T={t}, E={e}, P={p_met}\n  {gantt}"

# algoritmo spn: va primero el proceso mas cortito que este esperando
def spn(procesos_orig):
    lista = [Proceso(p.nombre, p.llegada, p.tiempo) for p in procesos_orig]
    tiempo, gantt, terminados = 0, "", 0 #variables para control
    n = len(lista)
    finalizados = [] #lista para meter los que ya acabaron
    
    while terminados < n:
        #buscamos que procesos ya estan en la fila y no han acabado
        disponibles = [p for p in lista if p.llegada <= tiempo and p.restante > 0]
        if not disponibles:
            tiempo += 1
            continue
        
        #de los que estan en la fila elegimos al que dure menos tiempo
        p = min(disponibles, key=lambda x: x.tiempo)
        for _ in range(p.tiempo):
            gantt += p.nombre
            tiempo += 1
        p.final = tiempo
        p.restante = 0
        terminados += 1
        finalizados.append(p) #lo guardamos en la lista de terminados
        
    t, e, p_met = calcular_metricas(finalizados) #sacamos metricas
    return f"SPN: T={t}, E={e}, P={p_met}\n  {gantt}"

#algoritmo round robin: reparte el tiempo en rebanadas iguales
def rr(procesos_orig, q):
    lista = [Proceso(p.nombre, p.llegada, p.tiempo) for p in procesos_orig]
    lista.sort(key=lambda x: x.llegada) #ordenamos por llegada
    tiempo, gantt, terminados = 0, "", 0
    cola, n, idx = [], len(lista), 0 #cola es la fila de espera
    
    while terminados < n:
        #metemos a la fila los procesos conforme van llegando
        while idx < n and lista[idx].llegada <= tiempo:
            cola.append(lista[idx]); idx += 1
        if not cola:
            tiempo += 1; continue #si no hay nadie esperamos
            
        p = cola.pop(0) #sacamos al primero de la fila
        atender = min(p.restante, q) #vemos si usa todo el quantum o menos
        for _ in range(atender):
            gantt += p.nombre
            tiempo += 1
            p.restante -= 1
            #revisamos si llego alguien nuevo mientras el proceso trabajaba
            while idx < n and lista[idx].llegada <= tiempo:
                cola.append(lista[idx]); idx += 1
        
        if p.restante > 0: cola.append(p) #si no acabo lo mandamos al final de la fila
        else: p.final = tiempo; terminados += 1 #si acabo anotamos su salida
            
    t, e, p_met = calcular_metricas(lista)
    return f"RR{q}: T={t}, E={e}, P={p_met}\n  {gantt}"

#algoritmo feedback: usa varias filas para castigar procesos largos
def fb(procesos_orig):
    lista = [Proceso(p.nombre, p.llegada, p.tiempo) for p in procesos_orig]
    lista.sort(key=lambda x: x.llegada)
    tiempo, gantt, terminados = 0, "", 0
    n, idx = len(lista), 0
    #creamos tres colas con diferentes prioridades
    q0, q1, q2 = [], [], []
    
    while terminados < n:
        #los nuevos siempre entran a la cola 0 (maxima prioridad)
        while idx < n and lista[idx].llegada <= tiempo:
            q0.append(lista[idx]); idx += 1
            
        #intentamos sacar proceso de la cola 0, luego la 1 y al final la 2
        if q0: p, cola_actual, sig_cola = q0.pop(0), q0, q1
        elif q1: p, cola_actual, sig_cola = q1.pop(0), q1, q2
        elif q2: p, cola_actual, sig_cola = q2.pop(0), q2, q2
        else: tiempo += 1; continue #si no hay nadie el tiempo corre
            
        gantt += p.nombre #ponemos la letra en el dibujo
        tiempo += 1 #el proceso usa solo 1 segundo de cpu
        p.restante -= 1 #le quitamos un segundo de trabajo
        
        #revisamos si llegaron nuevos a la cola 0
        while idx < n and lista[idx].llegada <= tiempo:
            q0.append(lista[idx]); idx += 1
            
        if p.restante > 0: sig_cola.append(p) #si no acabo, baja de nivel de prioridad
        else: p.final = tiempo; terminados += 1 #si acabo, se va del sistema
            
    t, e, p_met = calcular_metricas(lista)
    return f"FB: T={t}, E={e}, P={p_met}\n  {gantt}"

#para inventar procesos con datos al azar
def generar_ronda(n=5):
    nombres = "ABCDE" #letras para los procesos
    llegada = 0 #tiempo de inicio
    ronda = [] #guardamos los 5 procesos
    for i in range(n):
        duracion = random.randint(2, 6) #cada proceso dura entre 2 y 6 seg.
        ronda.append(Proceso(nombres[i], llegada, duracion))
        llegada += random.randint(0, 3) #el siguiente llega un poquito despues
    return ronda

for i in range(1, 6): # mostraremos 5 rondas
    ronda = generar_ronda() #creamos los procesos al azar
    info = "; ".join([f"{p.nombre}: {p.llegada}, t={p.tiempo}" for p in ronda])
    print(f"- Ronda {i}:")
    print(f"  {info}")
    print(f"  {fcfs(ronda)}")
    print(f"  {rr(ronda, 1)}")
    print(f"  {rr(ronda, 4)}")
    print(f"  {spn(ronda)}")
    print(f"  {fb(ronda)}")
    print("-" * 30)