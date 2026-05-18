import os
import signal
import sys

# Funcion para limpiar los procesos que ya terminaron
def recolectar_procesos_terminados(sig, frame):
    try:
        while True:
            # -1 indica cualquier hijo, WNOHANG evita que el padre se bloquee
            pid_acabado, status = os.waitpid(-1, os.WNOHANG)
            if pid_acabado <= 0:
                break
    except OSError:
        pass

# Configuracion de señales (Solo para Linux/Unix)
if os.name != 'nt':
    signal.signal(signal.SIGCHLD, recolectar_procesos_terminados)
    signal.signal(signal.SIGINT, signal.SIG_IGN)

def main():
    if os.name == 'nt':
        print("AVISO: El sistema operativo actual es Windows.")
        print("Las funciones 'os.fork' y 'SIGCHLD' no estan disponibles en este entorno.")
        print("Para verificar el funcionamiento, utilice un entorno Linux.\n")

    while True:
        try:
            # Nombre de mi minishell: Terminal !
            entrada = input("terminal> ")
            
            datos = entrada.split()
            if not datos:
                continue
            
            if datos[0] == "exit":
                print("Cerrando la terminal...")
                break

            # Intentar ejecutar el comando mediante fork
            try:
                p_id = os.fork()
            except AttributeError:
                print("Error: El sistema actual no soporta la llamada os.fork.")
                continue

            if p_id == 0:
                # Este es el proceso Hjo
                # Restaurar comportamiento de Ctrl+C para el comando
                signal.signal(signal.SIGINT, signal.SIG_DFL)
                try:
                    os.execvp(datos[0], datos)
                except FileNotFoundError:
                    print(f"Error: No se encontro el comando '{datos[0]}'")
                    os._exit(1)
            else:
                # Aquì el proceso padres
                # Espera sincronica para mantener el orden del prompt
                os.waitpid(p_id, 0)

        except EOFError:
            print("\nSaliendo...")
            break
        except Exception as e:
            print(f"Error durante la ejecucion: {e}")

if __name__ == "__main__":
    main()