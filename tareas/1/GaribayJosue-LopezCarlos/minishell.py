import os
import signal
import sys
import shlex

def sigchld_handler(signum, frame):
    # Manejador para recolectar procesos hijos de forma asincronica
    try:
        # WNOHANG evita que el padre se bloquee si no hay hijos terminados
        while True:
            pid, status = os.waitpid(-1, os.WNOHANG)
            if pid == 0:
                break
            # Procesar terminación del hijo
    except ChildProcessError:
        pass

def main():
# Se configuran las seniales necesarias
    # Instruccion para que la minishell ignore el Ctrl+C para que no se cierre
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    # Conectamos la senial SIGCHLD con la funcion sigchld_handler
    signal.signal(signal.SIGCHLD, sigchld_handler)

    # Bucle principal
    while True:
        try:
            # Instruccion para pedirle al usuario que ingrese un comando
            comando = input("\nminishell $ ")
            if not comando:
                continue

            # Separando las palabras del comando y guardandolas cada una en un arreglo
            arg = shlex.split(comando)

            # Verificando si el comando ingresado es exit (salir de la minishell)
            if arg[0] == "exit":
                print("saliendo de minishell...")
                break

            # Crear el proceso hijo
            # idProc es el identificador del proceso
            pid = os.fork()

            if pid == 0:
                # Ejecucion dentro del hijo
                # Instruccion para hacer que Ctrl+C vuelva a funcionar
                signal.signal(signal.SIGINT, signal.SIG_DFL)

                try:
                    # Instruccion para cambiar este proceso por el programa solicitado
                    os.execvp(arg[0], arg)

                except FileNotFoundError:
                    print(f"comando no encontrado: {arg[0]}")
                    sys.exit(1)
            else:
                # Ejecucion dentro del padre
                # El padre espera hasta que el hijo termine la tarea
                os.waitpid(pid, 0)

        except EOFError:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
    