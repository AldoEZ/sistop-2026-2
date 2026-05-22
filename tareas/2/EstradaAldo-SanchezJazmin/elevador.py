import time
import random
import threading

NUM_PISOS = 5
# nombres de amigos :)
nombres = ['Jaz', 'Aldo', 'Emir', 'Eve', 'Erick', 'Carrillo', 'Isaac', 'Nando', 'Fersa', 'Flacon']

# clase elevador, que es hija de clase Thread para poder manejarlo como hilo
class Elevador(threading.Thread):
    def __init__(self, num_pisos):
        super().__init__()
        self.capacidad = 5
        self.piso_actual = 0
        self.direccion = 1 # 1 si sube, -1 si baja
        self.mov_misma_direccion=0
        self.max_mov=5
        self.pasajeros = []
        self.lock_elevador = threading.Lock()
        self.solicitudes_por_piso = dict()
        self.puerta_abierta = False
        self.num_pisos = num_pisos
        self.funcionando = True
        self.semaforo_capacidad = threading.BoundedSemaphore(self.capacidad)
        self.condicion_movimiento = threading.Condition(self.lock_elevador)
        self.condicion_subida = threading.Condition(self.lock_elevador)
    
    # al hacer start el metodo run se inicia automaticamente 
    # se define el funcionamiento principal del elevador
    def run(self):
        while self.funcionando:
            with self.lock_elevador:
                if not self.funcionando:
                    break
                
                hay_solicitudes = any(len(personas) > 0 for personas in self.solicitudes_por_piso.values())
                hay_pasajeros = len(self.pasajeros) > 0
                
                if not hay_solicitudes and not hay_pasajeros:
                    if self.piso_actual != 0:
                        self.direccion = -1
                        self.piso_actual = 0
                        print(f"\nElevador -> No hay solicitues. Moviendo al piso 1, a esperar...")
                    else:
                        print("\nElevador -> Esperando solicitudes en piso 1...")
                        self.condicion_subida.wait(timeout=5.0)
                    continue
                
                pasajeros_bajando = [pasajero for pasajero in self.pasajeros if pasajero[1] == self.piso_actual]
                if pasajeros_bajando:
                    self.puerta_abierta = True
                    print(f"\nElevador -> Piso {self.piso_actual+1}: Hay que bajar a los chicos :(...")
                    for pasajero in pasajeros_bajando:
                        self.pasajeros.remove(pasajero)
                        self.semaforo_capacidad.release()
                        print(f"   Bajada -> {nombres[pasajero[0]]} bajó en el piso {self.piso_actual+1}, digan adios...")
                    time.sleep(1)
                
                if self.piso_actual in self.solicitudes_por_piso and self.solicitudes_por_piso[self.piso_actual]:
                    self.puerta_abierta = True
                    print(f"\nElevador -> Piso {self.piso_actual+1}: Hay que subir a los chicos :)...")
                    
                    lugares = self.capacidad - len(self.pasajeros)
                    
                    if lugares > 0:
                        self.condicion_subida.notify_all()
                        self.condicion_subida.wait(timeout=2.0)
                
                self.puerta_abierta = False
                print(f"\nElevador -> Las puertas cerraron. Num. de pasajeros: {len(self.pasajeros)}")
                
                proximos_pisos = []
                
                for p, personas in self.solicitudes_por_piso.items(): 
                    if personas:
                        proximos_pisos.append(p)
                
                for (_, p) in self.pasajeros:
                    proximos_pisos.append(p)
                #minimizar varios movimientos en sólo unos pisos
                if self.mov_misma_direccion>= self.max_mov:
                    self.direccion *= -1
                    self.mov_misma_direccion = 0
                
                if not proximos_pisos:
                    if self.piso_actual == self.num_pisos - 1:
                        self.direccion = -1
                    elif self.piso_actual == 0:
                        self.direccion = 1
                else:
                    if self.direccion == 1:
                        if not any(p > self.piso_actual for p in proximos_pisos):
                            self.direccion = -1
                    else:
                        if not any(p < self.piso_actual for p in proximos_pisos):
                            self.direccion = 1
                
                next_piso = self.piso_actual + self.direccion
                next_piso = max(0, min(self.num_pisos - 1, next_piso))
            
            time.sleep(1)
            with self.lock_elevador:
                self.piso_actual = next_piso
                #se cuentan los movimientos
                self.mov_misma_direccion += 1
                #notificar que ya cambiamos de piso
                self.condicion_movimiento.notify_all()
    
    # metodo para poder terminar la ejecucion
    def detener(self):
        with self.lock_elevador: 
            self.funcionando = False
            self.condicion_subida.notify_all()
            self.condicion_movimiento.notify_all()

# funcionamiento principal de un pasajero
def comportamiento_pasajero(id_persona, elevador):
    piso_actual = random.randint(0, elevador.num_pisos - 1)
    piso_destino = random.randint(0, elevador.num_pisos - 1)
    while piso_destino == piso_actual:
        piso_destino = random.randint(0, elevador.num_pisos - 1)
    
    print(f" Solicitud -> {nombres[id_persona]} esta en el piso {piso_actual+1} y su destino es el piso {piso_destino+1}")
    time.sleep(random.random())
    
    with elevador.lock_elevador:
        if piso_actual not in elevador.solicitudes_por_piso:
            elevador.solicitudes_por_piso[piso_actual] = []
        elevador.solicitudes_por_piso[piso_actual].append(id_persona)
    
    while piso_actual != piso_destino and elevador.funcionando:
        with elevador.lock_elevador:
            while (elevador.piso_actual != piso_actual or not elevador.puerta_abierta) and elevador.funcionando:
                elevador.condicion_subida.wait(timeout=1.0)
            
            if not elevador.funcionando:
                return
            #la solicitud ya sólo busca el id de la persona
            mi_solicitud = next(
                (s for s in elevador.solicitudes_por_piso.get(piso_actual, []) if s == id_persona),
                None
            )
            
            if mi_solicitud is not None:
                if elevador.semaforo_capacidad.acquire(blocking=False):
                    elevador.solicitudes_por_piso[piso_actual].remove(mi_solicitud)
                    elevador.pasajeros.append((id_persona, piso_destino))
                    elevador.condicion_subida.notify_all()
                    print(f"  Entrada -> {nombres[id_persona]} subió en piso {elevador.piso_actual+1}, digan hola...")
                    
                    while elevador.piso_actual != piso_destino and elevador.funcionando:
                        elevador.condicion_movimiento.wait(timeout=1.0)
                    
                    if elevador.piso_actual == piso_destino:
                        print(f"    Llegada -> {nombres[id_persona]} bajó justo en el piso {elevador.piso_actual+1}, otro adios...")
                        return
                else:
                    print(f"Advertencia -> El elevador esta lleno y {nombres[id_persona]} se quedo esperando en el piso {elevador.piso_actual+1}...")
                    elevador.condicion_subida.wait(timeout=1.0)      

if __name__ == "__main__":
    personas = 10
    duracion_funcionamiento = 50
    
    elevador = Elevador(NUM_PISOS)
    elevador.start()
    
    hilos_pasajeros = []
    for i in range(personas):
        pasajero = threading.Thread(target=comportamiento_pasajero, args=(i, elevador))
        pasajero.start()
        
        hilos_pasajeros.append(pasajero)
        time.sleep(random.uniform(2,4))
    
    time.sleep(duracion_funcionamiento)
    
    elevador.detener()
    
    elevador.join()
    
    for hilo in hilos_pasajeros:
        hilo.join()
