# Tarea 3. Algoritmos de Planificación de Procesos
# Autores: Gonzalez Falcon Luis Adrían & Lopez Morales Fernando Samuel
# 16-04-2026

import random
import sys

#Constante que define el número de rondas
NUM_RONDAS = 5

# Funcion para generar una carga aleatoria de 5 procesos
# return: una lista de diccionarios con la informacion de cada proceso
def generar_procesos():
    procesos= []
    tiempo_llegada= 0
    # lista_nombres = ["A", "B", "C", "D", "E"] # versino inicial
    
    for i in range(5):
        # Nombres de A a E usando ascii
        nombre= chr(65 + i) 
        t_cpu= random.randint(2, 8)
        
        # Se guarda la info en un diccionario sencillo -> se puede mejorar implementando objetos O.o
        proceso= {
            "nombre": nombre,
            "llegada": tiempo_llegada,
            "t": t_cpu,
            "restante": t_cpu,
            "tiempo_fin": 0
        }
        procesos.append(proceso)
        
        # El siguiente llega un poco despues
        tiempo_llegada= tiempo_llegada+random.randint(0, 3)
        
    return procesos

# FUncion para crear un proceso simple

def crear_proceso(nombre, t_llegada, t_cpu):
    proceso = {
        "nombre": nombre,
        "llegada": t_llegada,
        "t": t_cpu,
        "restante": t_cpu,
        "tiempo_fin": 0
    }
    return proceso

# Funcion para calcular las metricas finales y presentarlas
# Recibe: el nombre del algoritmo, la lista de procesos terminados y la cadena de ejecucion
# return: voidcito, solo imprime los resultados
def imprimir_resultados(nombre_algo, procesos_terminados, esquema_visual):
    suma_t = 0
    suma_e = 0
    suma_p = 0
    cantidad = len(procesos_terminados)
    
    for p in procesos_terminados:

        t_total=p["tiempo_fin"] - p["llegada"]
        e_espera=t_total - p["t"]
        p_penalizacion=t_total / p["t"]
        
        suma_t=suma_t + t_total
        suma_e=suma_e + e_espera
        suma_p=suma_p + p_penalizacion
        
        # print("Metricas de", p["nombre"], ": T=", t_total, "E=", e_espera) # debug de metricas individuales

    promedio_t=suma_t / cantidad
    promedio_e=suma_e / cantidad
    promedio_p=suma_p / cantidad
    
    # Imprimimos formateando a 2 decimales
    print("  " + nombre_algo + ": T={:.2f}, E={:.2f}, P={:.2f}".format(promedio_t, promedio_e, promedio_p))
    print("  " + esquema_visual)


# --- ALGORITMOS DE PLANIFICACION ---

# Algoritmo FCFS (First Come, First Serve)
# Recibe: lista original de procesos
# return: procesos terminados y string visual
def algoritmo_fcfs(procesos_originales):
    # Hacemos una copia manual para no afectar la lista original
    procesos = []
    for p in procesos_originales:
        procesos.append(p.copy())
        
    tiempo_actual = 0
    esquema_visual = ""
    terminados = []
    
    for p in procesos:
        # Si la CPU esta libre y el proceso aun no llega, el tiempo avanza
        if tiempo_actual < p["llegada"]:
            # esquema_visual = esquema_visual + "-" # opcional para mostrar tiempo muerto
            tiempo_actual = p["llegada"]
            
        # Ejecucion ininterrumpida
        for i in range(p["t"]):
            esquema_visual = esquema_visual + p["nombre"]
            tiempo_actual = tiempo_actual + 1
            
        p["tiempo_fin"] = tiempo_actual
        terminados.append(p)
        
    return terminados, esquema_visual


# Algoritmo Round Robin
# Recibe: lista original de procesos y el valor del quantum
def algoritmo_rr(procesos_originales, quantum):
    procesos = []
    for p in procesos_originales:
        procesos.append(p.copy())
        
    tiempo_actual= 0
    esquema_visual= ""
    terminados= []
    cola_listos= []
    
    # Variables para saber cuales ya entraron a la cola
    agregados=[]
    
    while len(terminados) < len(procesos):
        # if tiempo_actual > 100: break # prototipo de seguridad para que no se cicle
        
        # Agregamos a la cola los que van llegando
        for p in procesos:
            if p["llegada"] <= tiempo_actual and p["nombre"] not in agregados:
                cola_listos.append(p)
                agregados.append(p["nombre"])
                
        if len(cola_listos) == 0:
            tiempo_actual = tiempo_actual + 1
            continue
            
        # Sacamos el primero de la cola
        p_actual = cola_listos.pop(0)
        
        # Vemos cuanto tiempo se va a ejecutar (lo que le falte o el quantum)
        tiempo_a_usar= quantum
        if p_actual["restante"] < quantum:
            tiempo_a_usar= p_actual["restante"]
            
        # Ejectamos
        for i in range(tiempo_a_usar):
            esquema_visual= esquema_visual + p_actual["nombre"]
            tiempo_actual= tiempo_actual + 1
            p_actual["restante"]= p_actual["restante"] - 1
            
            # Revisamos si llegaron nuevos mientras este se ejecutaba
            for p_nuevo in procesos:
                if p_nuevo["llegada"] == tiempo_actual and p_nuevo["nombre"] not in agregados:
                    cola_listos.append(p_nuevo)
                    agregados.append(p_nuevo["nombre"])
        
        # Si ya termino, lo guardamos
        if p_actual["restante"] == 0:
            p_actual["tiempo_fin"]= tiempo_actual
            terminados.append(p_actual)
        else:
            # Si no, return al final de la cola
            cola_listos.append(p_actual)
            
    # print("fin rr", esquema_visual)
    return terminados, esquema_visual


# SPN (Shortest Process Next)
def algoritmo_spn(procesos_originales):
    procesos=[]
    for p in procesos_originales:
        procesos.append(p.copy())
        
    tiempo_actual= 0
    esquema_visual= ""
    terminados= []
    
    while len(procesos) > 0:
        disponibles= []
        for p in procesos:
            if p["llegada"] <= tiempo_actual:
                disponibles.append(p)
                
        if len(disponibles) == 0:
            tiempo_actual= tiempo_actual+1
            continue

        #Se busca el que tenga menor tiempo total y se inicializa con el primero disponible
        p_elegido = disponibles[0]
        for p in disponibles:
            if p["t"]<p_elegido["t"]:
                p_elegido=p

        for i in range(p_elegido["t"]):
            esquema_visual= esquema_visual+p_elegido["nombre"]
            tiempo_actual=tiempo_actual+1
            
        p_elegido["tiempo_fin"]=tiempo_actual
        terminados.append(p_elegido)
        procesos.remove(p_elegido)
        
    return terminados, esquema_visual


# FB
# tres colas de priorirdad con quantum de 1
def algoritmo_fb(procesos_originales):
    procesos= []
    for p in procesos_originales:
        procesos.append(p.copy())
        
    tiempo_actual= 0
    esquema_visual= ""
    terminados= []
    
    cola_alta= []
    cola_media= []
    cola_baja= []
    agregados= []
    
    while len(terminados)< len(procesos_originales):
        #Meter nuevos proceso a la cola
        for p in procesos:
            if p["llegada"] <= tiempo_actual and p["nombre"] not in agregados:
                cola_alta.append(p)
                agregados.append(p["nombre"])
                
        #Decidir la cola para sacar el proceso
        p_actual = None
        origen = 0        
        if len(cola_alta) > 0:
            p_actual = cola_alta.pop(0)
            origen = 1
        elif len(cola_media) > 0:
            p_actual = cola_media.pop(0)
            origen = 2
        elif len(cola_baja) > 0:
            p_actual = cola_baja.pop(0)
            origen = 3
            
        if p_actual == None:
            tiempo_actual = tiempo_actual + 1
            continue
            
        #1 unidad de tiempo
        esquema_visual = esquema_visual + p_actual["nombre"]
        tiempo_actual = tiempo_actual + 1
        p_actual["restante"] = p_actual["restante"] - 1
        
        #Lllegadas en esa unidad de tiempo: 
        for p_nuevo in procesos:
            if p_nuevo["llegada"] == tiempo_actual and p_nuevo["nombre"] not in agregados:
                cola_alta.append(p_nuevo)
                agregados.append(p_nuevo["nombre"])
                
        if p_actual["restante"] == 0:
            p_actual["tiempo_fin"]= tiempo_actual
            terminados.append(p_actual)
        else:
            #bajando de cola
            if origen == 1:
                cola_media.append(p_actual)
            elif origen == 2:
                cola_baja.append(p_actual)
            else:
                cola_baja.append(p_actual) # se queda en la mas baja
                
    return terminados, esquema_visual


# Funcion principal para llamar las demas
#rondas:numero de rondas
def iniciar(rondas, carga=None):
    print("Iniciando simulador de planificacion de procesos...\n")
    for r in range(rondas):
        print("- Ronda", r + 1, ":")
        
        # Usando variable auxiliar
        if carga is None:
            carga_actual = generar_procesos()
        else:
            carga_actual = carga
        
        # Usando siempre variable carga_actual para generar texto
        texto_carga= ""
        suma_tiempos= 0
        for p in carga_actual:
            texto_carga= texto_carga + p["nombre"] + ": " + str(p["llegada"]) + ", t=" + str(p["t"]) + "; "
            suma_tiempos= suma_tiempos + p["t"]
            
        print("  " + texto_carga + " (tot:" + str(suma_tiempos) + ")")
        
        # Ejecucion FCFS
        terminados, visual = algoritmo_fcfs(carga_actual)
        imprimir_resultados("FCFS", terminados, visual)
        
        # Ejecucion RR1
        terminados, visual = algoritmo_rr(carga_actual, 1)
        imprimir_resultados("RR1", terminados, visual)
        
        # Ejecucion RR4
        terminados, visual = algoritmo_rr(carga_actual, 4)
        imprimir_resultados("RR4", terminados, visual)
        
        # Ejecucion SPN
        terminados, visual = algoritmo_spn(carga_actual)
        imprimir_resultados("SPN", terminados, visual)
        
        # Ejecucion FB
        terminados, visual = algoritmo_fb(carga_actual)
        imprimir_resultados("FB", terminados, visual)
        
        print("\n")

#Inicio del programa
def main():
    if len(sys.argv) > 1:
        # TRY CATCH PARA mandar correctamente solo numreos
        try:
            rondas_a_ejecutar = int(sys.argv[1])
            iniciar(rondas_a_ejecutar)
            # print(rondas_a_ejecutar)
        except ValueError:
            print("Error: El argumento debe ser un numero. Usando default.")
            pass
    else:
        # Prueba del prof
        """
        procs = [crear_proceso('A', 0, 3),
                crear_proceso('B', 1, 5),
                crear_proceso('C', 3, 2),
                crear_proceso('D', 9, 5),
                crear_proceso('E', 12, 5)
        ]
        iniciar(NUM_RONDAS, procs)

    """
        iniciar(NUM_RONDAS)
main()