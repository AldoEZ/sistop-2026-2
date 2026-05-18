"""
Autores:
Santiago Arath Bello Sanchez
David Baruc López Romero
"""

import os
import sys
import signal
import shlex

def sigchld(signum, frame):
    """
    Manejador asíncrono para la señal SIGCHLD.
    Se ejecuta automáticamente cuando un proceso hijo termina.
    """
    try:
        # Bucle para recolectar a todos los hijos que hayan terminado.
        while True:
            # WNOHANG asegura que waitpid no bloquee el shell si no hay hijos muertos (zombies) listos.
            # -1 indica que espere a cualquier proceso hijo.
            pid, status = os.waitpid(-1, os.WNOHANG)
            if pid == 0:
                # pid 0 significa que hay hijos ejecutándose, pero ninguno ha cambiado de estado.
                break
    except ChildProcessError:
        # Se lanza esta excepción cuando ya no existen procesos hijos que esperar.
        pass

def main():
    # 5. Manejar SIGINT (Ctrl+C): El padre ignora la señal para no cerrarse.
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    
    # 4. Instalar el manejador de SIGCHLD para recolectar procesos en segundo plano/asíncronos.
    signal.signal(signal.SIGCHLD, sigchld)

    while True:
        try:
            # 1. Mostrar el prompt y esperar el comando
            user_input = input("minishell> ")
        except EOFError:
            # Manejo de Ctrl+D, Finaliza/mata la ejecucion del programa
            print("\nSaliendo...")
            break
        except KeyboardInterrupt:
            # Por seguridad, si el entorno relanza el Ctrl+C en input()
            print()
            continue

        # Si el usuario presiona Enter sin escribir nada, volvemos a mostrar el prompt
        if not user_input.strip():
            continue

        # 2. Leer la línea y separar programa de argumentos
        try:
            # shlex.split maneja correctamente espacios y comillas
            args = shlex.split(user_input)
        except ValueError as e:
            print(f"Error de sintaxis: {e}", file=sys.stderr)
            continue

        # 7. Manejar el comando interno 'exit'
        if args[0] == "exit":
            print("Terminando minishell...")
            break

        # 3. Ejecutar el comando
        try:
            pid = os.fork() # Creación del proceso hijo
        except OSError as e:
            print(f"Error al hacer fork: {e}", file=sys.stderr)
            continue

        if pid == 0:
            # --- CÓDIGO DEL PROCESO HIJO ---
            
            # Restaurar el comportamiento por defecto de Ctrl+C (SIGINT) en el hijo.
            # Esto permite que si hacemos 'sleep 10' y presionamos Ctrl+C, el hijo muera,
            # pero el shell padre siga vivo.
            signal.signal(signal.SIGINT, signal.SIG_DFL)
            
            try:
                # execvp busca automáticamente el ejecutable en el PATH del sistema
                os.execvp(args[0], args)
            except FileNotFoundError:
                print(f"minishell: {args[0]}: comando no encontrado", file=sys.stderr)
                os._exit(127) # Terminar el hijo limpiamente si falla el comando
            except Exception as e:
                print(f"minishell: error al ejecutar {args[0]}: {e}", file=sys.stderr)
                os._exit(1)
        else:
            # --- CÓDIGO DEL PROCESO PADRE ---
            # Como la recolección es asíncrona mediante el manejador SIGCHLD (punto 4),
            # el padre no llama a wait() de forma bloqueante aquí.
            # Simplemente continúa iterando el bucle y muestra el prompt de nuevo.
            pass
main()