"""
Simulación concurrente del elevador de FI-UNAM con interfaz en curses:
- Un hilo representa al elevador que se mueve entre pisos y atiende solicitudes
- Cada usuario es un hilo independiente que solicita el elevador desde un piso de origen a un destino
- Se usa sincronización real con Lock + Condition para coordinar el acceso a los datos compartidos
- La interfaz en curses muestra el estado del sistema en tiempo real, incluyendo:
  - Personas esperando en cada piso con su destino
  - El elevador con sus pasajeros actuales y dirección
  - Personas que ya llegaron a su destino, ordenados por tiempo de llegada
  - Un log de eventos recientes para entender qué está pasando
El sistema prioriza atender primero a los pasajeros que ya están a bordo, luego a los pisos con espera 
más antigua, y en caso de empate, al piso más cercano.
"""

from __future__ import annotations
import argparse
import random
import threading
import time
import curses
from collections import deque
from dataclasses import dataclass
from enum import Enum

# Constantes del sistema
NUM_PISOS = 5
CAPACIDAD_ELEVADOR = 5

# Clase para representar el estado de cada persona
class EstadoPersona(Enum):
    ESPERANDO = "esperando"
    A_BORDO = "a_bordo"
    LLEGO = "llego"

# Clase para representar a cada persona en el sistema
@dataclass
class Persona:
    pid: int
    origen: int
    destino: int
    llegada_solicitud: float
    estado: EstadoPersona = EstadoPersona.ESPERANDO
    subida_en: float | None = None
    bajada_en: float | None = None

# Clase principal que maneja la lógica del elevador y la coordinación entre hilos
class SistemaElevador:
    def __init__(self, total_personas: int, tiempo_piso: float):
        self.total_personas = total_personas
        self.tiempo_piso = tiempo_piso
        self.lock = threading.Lock()
        self.cond = threading.Condition(self.lock)

        self.piso_actual = 0
        self.direccion = 1  
        self.personas: dict[int, Persona] = {}
        self.esperando_por_piso = {p: deque() for p in range(NUM_PISOS)}
        self.a_bordo: list[int] = []

        self.creadas = 0
        self.atendidas = 0
        self.sim_inicio = time.time()
        self.ultimos_mensajes = deque(maxlen=5) # Para mostrar log en pantalla

    """
    Método para agregar un mensaje al log con timestamp relativo al inicio de la simulación 
    y mantener solo los últimos mensajes para mostrar en la interfaz de curses.
    """
    def log(self, mensaje: str) -> None:
        dt = time.time() - self.sim_inicio
        # Solo guarda los últimos mensajes para mostrarlos en curses
        self.ultimos_mensajes.append(f"[{dt:6.2f}s] {mensaje}")

    """
    Método para registrar a una persona que llega al sistema, 
    se agrega a la estructura de datos correspondiente y se 
    notifica al elevador para que pueda atenderla.
    """
    def registrar_persona(self, persona: Persona) -> None:
        with self.cond:
            self.personas[persona.pid] = persona
            self.esperando_por_piso[persona.origen].append(persona.pid)
            self.creadas += 1
            self.log(f"P{persona.pid:02d} llega a P{persona.origen + 1} va a P{persona.destino + 1}.")
            self.cond.notify_all()

    """
    Método para obtener los destinos internos actuales del elevador,
    si hay personas a bordo del elevador, se consideran como destinos internos 
    los pisos a los que esas personas quieren ir, de lo contrario, si no hay personas a bordo, 
    no hay destinos internos para el elevador, por lo que el elevador solo se enfocará en 
    atender los pisos con personas esperando.
    """
    def _destinos_internos(self) -> set[int]:
        return {self.personas[pid].destino for pid in self.a_bordo}

    """
    Método para obtener los pisos que tienen personas esperando, 
    si hay personas esperando en un piso, ese piso se considera "activo" para que 
    el elevador lo atienda, de lo contrario, si no hay personas esperando en ese piso, 
    el elevador no lo considerará como un destino a atender
    """
    def _pisos_con_espera(self) -> set[int]:
        return {p for p, cola in self.esperando_por_piso.items() if cola}

    """
    Método para calcular la prioridad de atender un piso específico, 
    se asigna una prioridad base de 0.0 a cada piso, luego se incrementa la prioridad en 50.0 
    si el piso es un destino interno (si hay personas a bordo que quieren ir a ese piso), 
    y se incrementa aún más la prioridad en función del tiempo que la persona más antigua ha 
    estado esperando en ese piso (el tiempo actual menos el tiempo de llegada de 
    la persona más antigua), lo que significa que los pisos con personas esperando por más tiempo 
    tendrán una prioridad más alta, finalmente, se calcula la distancia desde el piso actual del 
    elevador hasta el piso en cuestión y se devuelve una tupla con la prioridad total, 
    la distancia negativa (para priorizar pisos más cercanos) y el número de piso negativo 
    (para priorizar pisos más altos en caso de empate) que se utilizará para ordenar los pisos 
    candidatos a atender
    """
    def _prioridad_piso(self, piso: int, ahora: float) -> tuple[float, int, int]:
        destinos = self._destinos_internos()
        esperando = self._pisos_con_espera()
        prioridad = 0.0
        if piso in destinos:
            prioridad += 50.0
        if piso in esperando:
            cola = self.esperando_por_piso[piso]
            if cola:
                llegada_mas_antigua = min(self.personas[pid].llegada_solicitud for pid in cola)
                prioridad += ahora - llegada_mas_antigua
        distancia = abs(piso - self.piso_actual)
        return (prioridad, -distancia, -piso)

    """
    Método para seleccionar el próximo piso objetivo al que el elevador se dirigirá,
    se obtiene el conjunto de pisos candidatos que son aquellos que tienen personas a bordo
    que quieren ir a ese piso o que tienen personas esperando, si no hay candidatos, se devuelve None,
    de lo contrario, se selecciona el piso con la prioridad más alta utilizando la función de
    prioridad definida
    """
    def _seleccionar_objetivo(self) -> int | None:
        candidatos = self._destinos_internos() | self._pisos_con_espera()
        if not candidatos: return None
        ahora = time.time()
        return max(candidatos, key=lambda p: self._prioridad_piso(p, ahora))

    """
    Método para manejar el proceso de bajada de personas en el piso actual del elevador,
    si no hay personas a bordo, no se realiza ninguna acción, de lo contrario, se verifica cada persona 
    a bordo para ver si su destino coincide con el piso actual
    """
    def _bajan(self) -> None:
        if not self.a_bordo: return
        salen = [pid for pid in self.a_bordo if self.personas[pid].destino == self.piso_actual]
        for pid in salen:
            self.a_bordo.remove(pid)
            persona = self.personas[pid]
            persona.estado = EstadoPersona.LLEGO
            persona.bajada_en = time.time()
            self.atendidas += 1
            self.log(f"P{pid:02d} baja en P{self.piso_actual + 1}.")

    """
    Método para manejar el proceso de subida de personas en el piso actual del elevador,
    se obtiene la cola de personas esperando en el piso actual, mientras haya personas esperando y
    el elevador no haya alcanzado su capacidad máxima, se permite subir a la persona más antigua en la cola,
    se actualiza su estado a "a bordo", se registra el tiempo de subida, se agrega a la lista de personas 
    a bordo y se registra el evento en el log
    """
    def _suben(self) -> None:
        cola = self.esperando_por_piso[self.piso_actual]
        while cola and len(self.a_bordo) < CAPACIDAD_ELEVADOR:
            pid = cola.popleft()
            persona = self.personas[pid]
            persona.estado = EstadoPersona.A_BORDO
            persona.subida_en = time.time()
            self.a_bordo.append(pid)
            self.log(f"P{pid:02d} sube en P{self.piso_actual + 1}.")

    """
    Método principal del hilo del elevador, se ejecuta en un bucle infinito donde el elevador realiza las 
    siguientes acciones:
    1. Baja a las personas que deben bajar en el piso actual
    2. Sube a las personas que están esperando en el piso actual, respetando la capacidad máxima
    3. Notifica a todos los hilos para que puedan reaccionar a los cambios de estado
    4. Verifica si ya se han atendido todas las personas, en cuyo caso finaliza la simulación
    5. Selecciona el próximo piso objetivo utilizando la función de prioridad, si no hay objetivos 
      disponibles, espera a que haya cambios en el sistema (nuevas personas o personas a bordo)
    6. Si hay un objetivo seleccionado, se mueve hacia ese piso, actualizando la dirección y el piso 
    actual después de un tiempo de viaje simulado por piso
    """
    def hilo_elevador(self) -> None:
        with self.cond:
            self.log("Elevador iniciado.")
        while True:
            with self.cond:
                self._bajan()
                self._suben()
                self.cond.notify_all()
                if self.atendidas >= self.total_personas:
                    self.log("Elevador finaliza.")
                    self.cond.notify_all()
                    return

                objetivo = self._seleccionar_objetivo()
                while objetivo is None:
                    self.cond.wait()
                    self._bajan()
                    self._suben()
                    self.cond.notify_all()
                    if self.atendidas >= self.total_personas:
                        self.log("Elevador finaliza.")
                        self.cond.notify_all()
                        return
                    objetivo = self._seleccionar_objetivo()

                if objetivo == self.piso_actual: continue

                paso = 1 if objetivo > self.piso_actual else -1
                self.direccion = paso
                prox = self.piso_actual + paso
                
            time.sleep(self.tiempo_piso)
            with self.cond:
                self.piso_actual = prox
                self.cond.notify_all()

    """
    Método principal del hilo de cada persona, 
    se crea una instancia de Persona con su información, se registra en el sistema,
    y luego espera a que su estado cambie de "esperando" a "a bordo" y finalmente a "llego", 
    utilizando la condición para esperar y ser notificado de los cambios de estado.
    """
    def hilo_persona(self, pid: int, origen: int, destino: int) -> None:
        persona = Persona(pid, origen, destino, time.time())
        self.registrar_persona(persona)
        with self.cond:
            while persona.estado == EstadoPersona.ESPERANDO:
                self.cond.wait()
            while persona.estado != EstadoPersona.LLEGO:
                self.cond.wait()

"""
Función auxiliar para generar un piso de destino aleatorio diferente al piso de origen,
se crea una lista de opciones que incluye todos los pisos excepto el piso actual,
y se selecciona uno al azar utilizando random.choice
"""
def piso_aleatorio_distinto(piso_actual: int) -> int:
    opciones = [p for p in range(NUM_PISOS) if p != piso_actual]
    return random.choice(opciones)

"""
Función para dibujar la interfaz de usuario utilizando curses, se actualiza en tiempo real para mostrar 
el estado del sistema, incluyendo las personas esperando en cada piso con su destino, el elevador con 
sus pasajeros actuales y dirección, las personas que ya llegaron a su destino ordenados por tiempo 
de llegada, y un log de eventos recientes para entender qué está pasando en el sistema, 
la interfaz se actualiza cada 50ms y se muestra un mensaje final cuando la simulación termina
"""

def dibujar_interfaz(stdscr, sistema):
    curses.curs_set(0) # Ocultar cursor
    stdscr.nodelay(1)  # No bloquear
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE) # Elevador
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK) # Terminados
    
    while True:
        stdscr.clear()
        with sistema.lock: # Lee estado protegido
            terminado = sistema.atendidas >= sistema.total_personas
            
            # Cabecera
            stdscr.addstr(0, 0, f"=== SIMULADOR DE ELEVADOR FI-UNAM ===", curses.A_BOLD)
            stdscr.addstr(1, 0, f"Personas atendidas: {sistema.atendidas} / {sistema.total_personas}")
            
            # Encabezados de columnas
            stdscr.addstr(3, 2, "ESPERANDO (-> DESTINO)", curses.A_UNDERLINE)
            stdscr.addstr(3, 40, "ELEVADOR", curses.A_UNDERLINE)
            stdscr.addstr(3, 65, "UBICACIÓN", curses.A_UNDERLINE)
            stdscr.addstr(3, 78, "YA LLEGARON", curses.A_UNDERLINE) # Nueva columna

            # Dibujar edificio
            for p in range(NUM_PISOS - 1, -1, -1):
                y = 5 + ((NUM_PISOS - 1 - p) * 2)
                
                # IZQUIERDA: Fila de espera con su destino
                esperan = []
                for pid in list(sistema.esperando_por_piso[p]):
                    destino_real = sistema.personas[pid].destino + 1
                    esperan.append(f"P{pid:02d}(->{destino_real})")
                
                espera_str = " ".join(esperan) if esperan else ""
                if len(espera_str) > 35:
                    espera_str = espera_str[:32] + "..."
                stdscr.addstr(y, 2, f"{espera_str:<35}")
                
                # CENTRO: Hueco del elevador
                if p == sistema.piso_actual:
                    pasajeros = [f"P{pid:02d}" for pid in sistema.a_bordo]
                    pas_str = ",".join(pasajeros)
                    dir_char = "▲" if sistema.direccion == 1 else "▼" if sistema.direccion == -1 else "-"
                    stdscr.addstr(y, 40, f"[ {dir_char} {pas_str:^15} ]", curses.color_pair(1))
                else:
                    stdscr.addstr(y, 40, f"[                   ]")

                # DERECHA: Nombre del piso
                stdscr.addstr(y, 65, f"<-- Piso {p+1}", curses.A_BOLD)

                # EXTREMO DERECHO: Personas que ya llegaron a este piso
                # Filtra a las personas que ya llegaron y cuyo destino final era este piso
                llegados = [
                    persona for persona in sistema.personas.values()
                    if persona.estado == EstadoPersona.LLEGO and persona.destino == p
                ]
                # Los ordenamos por el tiempo exacto en el que se bajaron
                llegados.sort(key=lambda x: x.bajada_en)
                
                # Formateamos la cadena (ej. P15 P07)
                llegados_str = " ".join([f"P{persona.pid:02d}" for persona in llegados])
                
                # Si son muchos, limita la cadena para que no se desborde la terminal
                if len(llegados_str) > 40:
                    llegados_str = "..." + llegados_str[-37:]
                
                stdscr.addstr(y, 78, llegados_str)
            
            # Log de eventos desplazado hacia abajo
            stdscr.addstr(17, 0, "--- Últimos Eventos ---", curses.A_BOLD)
            for i, msj in enumerate(sistema.ultimos_mensajes):
                stdscr.addstr(18 + i, 0, msj)
                
        stdscr.refresh()
        
        if terminado:
            stdscr.addstr(24, 0, "Simulación terminada. Presiona cualquier tecla para ver el resumen.", curses.color_pair(2))
            stdscr.nodelay(0) # Bloquear para esperar tecla
            stdscr.getch()
            break
            
        time.sleep(0.05) # Refresh rate de 20fps

"""
Función principal para ejecutar la simulación del elevador, se crea una instancia del sistema,
se inicia el hilo del elevador, se crean hilos para cada persona que llega al sistema, 
y se inicia la interfaz de curses para mostrar el estado en tiempo real, al finalizar la simulación 
se muestra un resumen final con los tiempos de espera y viaje de cada persona
"""             
def simular(args):
    sistema = SistemaElevador(total_personas=args.personas, tiempo_piso=args.tiempo_piso)
    
    t_elevador = threading.Thread(target=sistema.hilo_elevador, name="Elevador")
    t_elevador.start()

    personas_hilos = []
    
    """
    Función auxiliar para crear hilos de personas, se ejecuta en un hilo separado para no 
    bloquear la interfaz de curses, se generan personas con un origen y destino aleatorio, 
    se inicia el hilo de cada persona y se agrega a la lista de hilos,
    si se especifica un tiempo máximo de llegada, se espera un tiempo aleatorio entre 0 y ese máximo
    antes de crear la siguiente persona para simular llegadas
    """
    def crear_personas():
        for pid in range(1, args.personas + 1):
            origen = random.randrange(NUM_PISOS)
            destino = piso_aleatorio_distinto(origen)
            t = threading.Thread(target=sistema.hilo_persona, args=(pid, origen, destino))
            t.start()
            personas_hilos.append(t)
            if args.llegada_max > 0:
                time.sleep(random.uniform(0.0, args.llegada_max))
                
    # Hilo para crear personas para que no bloquee curses
    threading.Thread(target=crear_personas, daemon=True).start()

    # Iniciar interfaz
    curses.wrapper(dibujar_interfaz, sistema)

    # Esperar hilos para resumen
    for t in personas_hilos: t.join()
    t_elevador.join()
    
    # Imprimir resumen final en terminal normal
    print("\nResumen final")
    print("=" * 60)
    for pid in sorted(sistema.personas):
        p = sistema.personas[pid]
        espera = (p.subida_en - p.llegada_solicitud) if p.subida_en else 0.0
        viaje = (p.bajada_en - p.subida_en) if p.subida_en and p.bajada_en else 0.0
        total = (p.bajada_en - p.llegada_solicitud) if p.bajada_en else 0.0
        print(f"Persona {pid:02d}: P{p.origen + 1} -> P{p.destino + 1} | espera={espera:5.2f}s | viaje={viaje:5.2f}s | total={total:5.2f}s")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--personas", type=int, default=10)
    parser.add_argument("--tiempo-piso", type=float, default=0.5)
    parser.add_argument("--llegada-max", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=20260326)
    args = parser.parse_args()
    
    random.seed(args.seed)
    simular(args)