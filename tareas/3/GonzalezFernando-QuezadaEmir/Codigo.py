import random

class Proceso:
    def __init__(self, nombre, llegada, servicio):
        self.nombre = nombre
        self.llegada = llegada
        self.servicio = servicio
        self.restante = servicio
        self.finalizacion = 0
        self.inicio_ejecucion = -1

    def __repr__(self):
        return f"{self.nombre}: {self.llegada}, t={self.servicio}"

def calcular_metricas(procesos):
    n = len(procesos)
    # Tiempo de retorno (T)
    retorno = 0
    # Tiempo de espera (E)
    espera = 0
    # Indice de penalizacion (P)
    penalizacion = 0
    for it in procesos:
        retorno += (it.finalizacion - it.llegada)
        espera += it.servicio
        penalizacion += (it.finalizacion - it.llegada) / it.servicio
    return (round(retorno/n, 2), round((retorno-espera)/n, 2), round(penalizacion/n, 2))


# --- ALGORITMOS ---

def fcfs(procesos_in):
    procesos = sorted([Proceso(p.nombre, p.llegada, p.servicio) for p in procesos_in], key=lambda x: x.llegada)
    tiempo = 0
    s = ""
    # Atendemos los procesos estrictamente en el orden en que llegaron
    for p in procesos:
        if tiempo < p.llegada:
            # Si el CPU esta echando hueva, adelantamos el reloj hasta que llegue el siguiente
            s += "." * (p.llegada - tiempo)
            tiempo = p.llegada
        
        # El proceso se ejecuta completo sin interrupciones
        s += p.nombre * p.servicio
        tiempo += p.servicio
        p.finalizacion = tiempo
    return s, procesos

def spn(procesos_in):
    procesos = [Proceso(p.nombre, p.llegada, p.servicio) for p in procesos_in]
    tiempo = 0
    s = ""
    terminados = []
    
    while len(terminados) < len(procesos):
        # Filtramos solo a los procesos que ya llegaron y que aun no han terminado
        disponibles = [p for p in procesos if p.llegada <= tiempo and p not in terminados]
        if not disponibles:
            s += "."
            tiempo += 1
            continue
        
        # De los que estan esperando, elegimos al que requiera menos tiempo (Porque nos caen mal los q se tardan)
        proximo = min(disponibles, key=lambda x: x.servicio)
        
        # Al igual que FCFS, no hay interrupciones. Se ejecuta hasta acabar
        s += proximo.nombre * proximo.servicio
        tiempo += proximo.servicio
        proximo.finalizacion = tiempo
        terminados.append(proximo)
    return s, terminados

def round_robin(procesos_in, q):
    procesos = sorted([Proceso(p.nombre, p.llegada, p.servicio) for p in procesos_in], key=lambda x: x.llegada)
    tiempo = 0
    s = ""
    cola = []
    terminados = []
    lista_espera = procesos[:]

    while len(terminados) < len(procesos):
        #" Todos los que acaban de llegar en este segundo se forman en la cola
        while lista_espera and lista_espera[0].llegada <= tiempo:
            cola.append(lista_espera.pop(0))

        if not cola:
            s += "."
            tiempo += 1
            continue

        p = cola.pop(0)
        # El proceso se ejecuta un maximo de 'q' veces. Si le falta menos, sale antes
        ejecutar = min(p.restante, q)
        s += p.nombre * ejecutar
        p.restante -= ejecutar

        # Si mientras este proceso se ejecutaba llegaron otros, los formamos primero
        for it in range(1, ejecutar + 1):
            while lista_espera and lista_espera[0].llegada == tiempo + it:
                cola.append(lista_espera.pop(0))

        tiempo += ejecutar
        if p.restante > 0:
            # Si se le acabó el quantum y no terminó, lo mandamos al final de la cola
            cola.append(p)
        else:
            # Si termino su tiempo de servicio requerido, se retira caballerosamente
            p.finalizacion = tiempo
            terminados.append(p)

    return s, terminados

def feedback(procesos_in, q=1):
    # FB con 3 colas de prioridad (Q0, Q1, Q2)
    procesos = sorted([Proceso(p.nombre, p.llegada, p.servicio) for p in procesos_in], key=lambda x: x.llegada)
    tiempo = 0
    resultadoRonda = ""
    colas = [[], [], []]  # Prioridad 0 (alta), 1 (baja) y 2 (sumamente baja nadie los quiere)
    terminados = []
    lista_espera = procesos[:]

    while len(terminados) < len(procesos):
        #. Todo proceso nuevo entra directamente a la cola VIP (Q0) *
        while lista_espera and lista_espera[0].llegada <= tiempo:
            colas[0].append((lista_espera.pop(0), 0))

        p_data = None
        # El CPU siempre busca primero en las colas mas altas. Si Q0 tiene gente, ignora Q1 y Q2
        for i in range(3):
            if colas[i]:
                p_data = colas[i].pop(0)
                nivel_actual = i
                break

        if not p_data:
            resultadoRonda += "."
            tiempo += 1
            continue

        p, _ = p_data
        ejecutar = min(p.restante, q)
        resultadoRonda += p.nombre * ejecutar
        p.restante -= ejecutar

        # Registramos las llegadas durante la ejecucion (siempre a Q0)
        for t_inc in range(1, ejecutar + 1):
            while lista_espera and lista_espera[0].llegada == tiempo + t_inc:
                colas[0].append((lista_espera.pop(0), 0))

        tiempo += ejecutar
        if p.restante > 0:
            # Si no acabo, lo castigamos bajandolo a una cola inferior.
            # El min asegura que si ya esta en el pozo (Q2), ahi se quede
            nuevo_nivel = min(nivel_actual + 1, 2)
            colas[nuevo_nivel].append((p, nuevo_nivel))
        else:
            p.finalizacion = tiempo
            terminados.append(p)

    return resultadoRonda, terminados


def selfish_rr(procesos_in, a=2, b=1):
    # Selfish Round Robin: dos colas con prioridades numericas.
    # cola_aceptados: procesos que ya pueden usar el CPU, su prioridad crece "b" por tick.
    # cola_nuevos: recien llegados que aun no alcanzan la prioridad minima de los aceptados, su prioridad crece "a" por tick.
    # Un proceso nuevo se promueve a aceptados cuando su prioridad >= min(cola_aceptados).


    procesos = sorted([Proceso(p.nombre, p.llegada, p.servicio) for p in procesos_in], key=lambda x: x.llegada)
    tiempo = 0
    resultadoRonda = ""
    cola_nuevos = []     
    cola_aceptados = []  
    terminados = []
    lista_espera = procesos[:]

    actual = None
    prioridad_actual = 0
    contador_q = 1
    q = 1

    while len(terminados) < len(procesos):
        while lista_espera and lista_espera[0].llegada <= tiempo:
            p = lista_espera.pop(0)
            if len(cola_aceptados) == 0 and actual is None:
                # Si el sistema esta completamente vacio, las puertas estan abiertas y entra a aceptados
                cola_aceptados.append((0, p))
            else:
                # Si ya hay gente ejecutandose, los bloquean y se van a la sala de espera de nuevos
                cola_nuevos.append((0, p))

        if actual is None and cola_aceptados:
            prioridad_actual, actual = cola_aceptados.pop(0)

        if actual is not None:
            resultadoRonda += actual.nombre
            actual.restante -= 1
            # El proceso en ejecucion sigue aumentando su prioridad a ritmo 'b'
            prioridad_actual += b
        else:
            resultadoRonda += "."

        tiempo += 1

        # Identificamos la prioridad mas baja dentro de la fila activa para usarla como meta
        s_aceptados = len(cola_aceptados)
        if s_aceptados == 0:
            min_pri = prioridad_actual if actual is not None else 0
        else:
            min_pri = float('inf')

        nueva_aceptados = []
        for pri, p in cola_aceptados:
            nueva_pri = pri + b
            if nueva_pri < min_pri:
                min_pri = nueva_pri
            nueva_aceptados.append((nueva_pri, p))
        cola_aceptados = nueva_aceptados

        # Los castigados en espera acumulan prioridad mas rapido, a ritmo 'a'
        cola_nuevos = [(pri + a, p) for pri, p in cola_nuevos]

        pendientes = []
        for pri, p in cola_nuevos:
            # En el instante en que el coraje de un nuevo alcanza al menor de los aceptados, es promovido
            if pri >= min_pri:
                cola_aceptados.append((pri, p))
            else:
                pendientes.append((pri, p))
        cola_nuevos = pendientes

        if actual is not None and actual.restante == 0:
            actual.finalizacion = tiempo
            terminados.append(actual)
            actual = None
            contador_q = 0
        elif contador_q == q and actual is not None:
            # Los que ya estan en la zona activa se comportan como un Round Robin tradicional
            cola_aceptados.append((prioridad_actual, actual))
            actual = None
            contador_q = 0

        contador_q += 1

    return resultadoRonda, terminados




def generar_carga():
    n = 5
    nombres = "ABCDE"
    carga = []
    t_llegada = 0
    for i in range(n):
        t_llegada += random.randint(0, 3)
        t_servicio = random.randint(2, 6)
        carga.append(Proceso(nombres[i], t_llegada, t_servicio))
    return carga

def ejecutar_simulacion(rondas=5):
    algos = [
        ("FCFS",   lambda c: fcfs(c)),
        ("RR1",    lambda c: round_robin(c, 1)),
        ("RR4",    lambda c: round_robin(c, 4)),
        ("SPN",    lambda c: spn(c)),
        ("FB",     lambda c: feedback(c, 1)),
        ("SRR",    lambda c: selfish_rr(c, 2, 1)),
    ]

    for i in range(1, rondas + 1):
        carga = generar_carga()
        total = sum(p.servicio for p in carga)
        carga_str = "; ".join([f"{p.nombre}: {p.llegada}, t={p.servicio}" for p in carga])

        print(f"\n- Ronda {i}:")
        print(f"  {carga_str}")
        print(f"    (tot:{total})")

        for nombre, func in algos:
            resultadoRonda, terminados = func(carga)
            t, e, p = calcular_metricas(terminados)
            print(f"  {nombre}: T={t}, E={e}, P={p}")
            print(f"    {resultadoRonda}")

if __name__ == "__main__":
    ejecutar_simulacion(5)  