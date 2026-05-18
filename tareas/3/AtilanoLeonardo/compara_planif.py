import random

def calc_metricas(terminados):
    sum_T, sum_E, sum_P = 0, 0, 0
    n = len(terminados)

    for p in terminados:
        T = p['fin'] - p['lleg']
        E = T - p['rafaga']
        P = T / p['rafaga']
        sum_T += T
        sum_E += E
        sum_P += P

    return sum_T / n, sum_E / n, sum_P / n

def imprimir_res(nombre, terminados, linea):
    T, E, P = calc_metricas(terminados)
    print(f"  {nombre}: T={T:.1f}, E={E:.1f}, P={P:.2f}")
    print(f"  {linea}")


# ---------------- PLANIFICADORES ----------------

def planif_FCFS(procs_base):
    procs = [dict(p) for p in procs_base]
    t = 0
    linea = ""
    terminados = []

    while procs:
        disp = [p for p in procs if p['lleg'] <= t]

        if not disp:
            linea += "-"  # tiempo muerto
            t += 1
            continue

        actual = disp[0]

        linea += actual['id'] * actual['rest']
        t += actual['rest']
        actual['fin'] = t

        terminados.append(actual)
        procs.remove(actual)

    return terminados, linea


def planif_RR(procs_base, quantum):
    procs = [dict(p) for p in procs_base]
    t = 0
    linea = ""
    terminados = []
    cola = []
    agregados = set()

    while procs or cola:
        for p in procs:
            if p['lleg'] <= t and p['id'] not in agregados:
                cola.append(p)
                agregados.add(p['id'])

        if not cola:
            linea += "-"
            t += 1
            continue

        actual = cola.pop(0)
        t_ejec = min(actual['rest'], quantum)

        linea += actual['id'] * t_ejec
        t += t_ejec
        actual['rest'] -= t_ejec

        # metemos a los que acaban de llegar antes de volver a formar a este
        for p in procs:
            if p['lleg'] <= t and p['id'] not in agregados:
                cola.append(p)
                agregados.add(p['id'])

        if actual['rest'] == 0:
            actual['fin'] = t
            terminados.append(actual)
            procs.remove(actual)
        else:
            cola.append(actual)  # se vuelve a formar

    return terminados, linea


def planif_SPN(procs_base):
    procs = [dict(p) for p in procs_base]
    t = 0
    linea = ""
    terminados = []

    while procs:
        disp = [p for p in procs if p['lleg'] <= t]
        if not disp:
            linea += "-"
            t += 1
            continue

        # spn ordena por ráfaga restante
        disp.sort(key=lambda x: x['rest'])
        actual = disp[0]

        linea += actual['id'] * actual['rest']
        t += actual['rest']
        actual['fin'] = t
        terminados.append(actual)
        procs.remove(actual)

    return terminados, linea


# REFINAMIENTO (Multinivel FB)
def planif_FB(procs_base):
    procs = [dict(p) for p in procs_base]
    t = 0
    linea = ""
    terminados = []

    Q0, Q1, Q2 = [], [], []  # Q0 es la mas alta
    agregados = set()

    while procs or Q0 or Q1 or Q2:
        for p in procs:
            if p['lleg'] <= t and p['id'] not in agregados:
                Q0.append(p)
                agregados.add(p['id'])

        # print("revisando colas", Q0, Q1, Q2) # debugueando porque me fallaba el salto

        if Q0:
            actual = Q0.pop(0)
            q = 1
            sig_cola = Q1
        elif Q1:
            actual = Q1.pop(0)
            q = 2
            sig_cola = Q2
        elif Q2:
            actual = Q2.pop(0)
            q = 4
            sig_cola = Q2  # ya de aqui no baja
        else:
            linea += "-"
            t += 1
            continue

        t_ejec = min(actual['rest'], q)
        linea += actual['id'] * t_ejec
        t += t_ejec
        actual['rest'] -= t_ejec

        # OJO: aqui tenia un bug. hay q meter a los nuevos antes de mandar este a su nueva cola
        for p in procs:
            if p['lleg'] <= t and p['id'] not in agregados:
                Q0.append(p)
                agregados.add(p['id'])

        if actual['rest'] == 0:
            actual['fin'] = t
            terminados.append(actual)
            procs.remove(actual)
        else:
            sig_cola.append(actual)

    return terminados, linea


# ---------------- SIMULADOR ----------------

def gen_procesos(num_procs):
    procs = []
    t_llegada = 0
    nombres = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    for i in range(num_procs):
        raf = random.randint(2, 8)
        procs.append({
            'id': nombres[i],
            'lleg': t_llegada,
            'rafaga': raf,
            'rest': raf,
            'fin': 0
        })
        t_llegada += random.randint(0, 3)

    return procs


def run_rondas(num):
    for i in range(num):
        print(f"\n- Ronda {i + 1}:")
        procs = gen_procesos(5)

        txt_procs = "; ".join([f"{p['id']}: {p['lleg']}, t={p['rafaga']}" for p in procs])
        tot_t = sum(p['rafaga'] for p in procs)
        print(f"  {txt_procs} (tot:{tot_t})")

        comp, linea = planif_FCFS(procs)
        imprimir_res("FCFS", comp, linea)

        comp, linea = planif_RR(procs, 1)
        imprimir_res("RR1 ", comp, linea)

        comp, linea = planif_RR(procs, 4)
        imprimir_res("RR4 ", comp, linea)

        comp, linea = planif_SPN(procs)
        imprimir_res("SPN ", comp, linea)

        comp, linea = planif_FB(procs)
        imprimir_res("FB  ", comp, linea)


if __name__ == "__main__":
    print("--- COMPARADOR DE PLANIFICADORES ---")
    run_rondas(5)