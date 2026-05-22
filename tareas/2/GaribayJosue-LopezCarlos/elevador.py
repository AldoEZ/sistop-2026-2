import curses
import threading
import time
import random

#Definimos la cantdad maxima de usuarios que caben en el elevador 
CAPA_MAX= 5 

"""Clase Elevador: 
    En esta clase vamos a definir diferentes funciones que nos ejemplifican de mejor manera el funcionamiento del elevador 
    Desde cuantas personas caben, como abordan los usuarios el elevador y el como recorre los pisos. 
""" 
class Elevador: 
    #Esta función nos ayuda a definir las condiciones iniciales del elevador 
    def __init__(self): 
        #Condiciones iniciales del elevador 
        self.piso_actual = 0
        self.capacidad = CAPA_MAX
        self.pasajeros = [] 
        self.esperando = [[] for _ in range(CAPA_MAX)]
        self.direccion = 1
        
        #Condiciones de sincronización 
        self.lock = threading.Lock()
        self.cond_piso = [threading.Condition(self.lock) for _ in range(5)]
        self.cond_destino = [threading.Condition(self.lock) for _ in range(5)]

    #Función del flujo de usuarios en el elevador 
    def flujo_usuario(self, id_usr, origen, destino):
        with self.lock: 
            #Espera del usuario 
            self.esperando[origen].append(id_usr) 
            while not (self.piso_actual == origen and len(self.pasajeros) < self.capacidad):
                self.cond_piso[origen].wait()
            
            #El usuario entra al elevador 
            self.esperando[origen].remove(id_usr)
            self.pasajeros.append((id_usr, destino))
            
            #El hilo del usuario espera llegar a su destino 
            while self.piso_actual != destino:
                self.cond_destino[destino].wait()
            
            #Llega a su destino y libera el lugar 
            self.pasajeros = [p for p in self.pasajeros if p[0] != id_usr]
            self.cond_piso[self.piso_actual].notify_all()

    #Esta función nos ayuda a definir el movimiento del elevador para el refinamiento 
    #Aún dudo si es una buena solución, revisalo porfavor. 
    def movimiento_elevador(self): 
        #Tiempo de viaje 
        time.sleep(1) 
        with self.lock: 
            #Revisa si ya llego al piso final o inicial, y en caso afirmativo cambia su dirección. 
            if self.piso_actual == 4: self.direccion = -1
            elif self.piso_actual == 0: self.direccion = 1
            
            #Se mueve entre los pisos sumando y/o restando el valor de su posición actual con el valor de su posición 
            self.piso_actual += self.direccion
            # Despertar a los hilos correspondientes
            self.cond_destino[self.piso_actual].notify_all()
            self.cond_piso[self.piso_actual].notify_all()

#Función para la vista en curses 
def vista_curses(stdscr, elevador): 
    #Borramos el cursor 
    curses.curs_set(0)
    stdscr.nodelay(1)
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)

    while True:
        stdscr.erase()
        #Leemos el estado del elevador para imprimirlo
        with elevador.lock:
            stdscr.addstr(1, 2, "======== ELEVADOR ========", curses.A_BOLD)
            
            for i in range(4, -1, -1):
                y = 8 - (i * 1.5)
                #Representación visual del elevador 
                pos = " [E] " if elevador.piso_actual == i else "     "
                esperan = f"Esperando: {elevador.esperando[i]}"
                stdscr.addstr(int(y), 2, f"PISO {i+1} |{pos}| {esperan}")

            dentro = [f"U{p[0]}->P{p[1]+1}" for p in elevador.pasajeros]
            stdscr.addstr(11, 2, f"PASAJEROS DENTRO: {dentro}", curses.color_pair(1))
            stdscr.addstr(12, 2, f"DIRECCIÓN: {'SUBIENDO' if elevador.direccion == 1 else 'BAJANDO'}", curses.color_pair(2))
            stdscr.addstr(14, 2, "Pulsa 'x' para terminar la simulación.")

        stdscr.refresh() 
        #Frecuencia de actualización de la pantalla 
        time.sleep(0.05) 
        #Detenemos el programa si presionamos la tecla "x" 
        if stdscr.getch() == ord('x'):
            break

def main(stdscr):
    elevador = Elevador()

    #Función del hilo del elevador 
    def control_elevador():
        while True:
            elevador.movimiento_elevador() 
    threading.Thread(target=control_elevador, daemon=True).start()

    #Función de los hilos de los usuarios 
    def crear_usuarios():
        u_id = 0 
        #Aquí definimos la creación de hilos de los usuarios 
        #En si no definimos una cantidad especifica de hilos si no que se seguiran generando 
        #Si quieres hazle un for, para que definas cuantos quieres crear, pero igual puse que con "x" terminas la ejecución para que 
        #el programa no corra infinitamente 
        while True:
            time.sleep(random.uniform(1, 4))
            ori = random.randint(0, 4) 
            #Se genera un destino aleatorio diferente al origen 
            des = random.choice([p for p in range(5) if p != ori])
            threading.Thread(target=elevador.flujo_usuario, args=(u_id, ori, des), daemon=True).start()
            u_id += 1
    threading.Thread(target=crear_usuarios, daemon=True).start()

    vista_curses(stdscr, elevador)

if __name__ == "__main__":
    curses.wrapper(main)