import sys
import shlex
import os
import signal

# Manejador para limpiar procesos en background y evitar el SIGCHLD
def sigchld_handler(signum, frame):
    try:
        while True:
            # WNOHANG asegura que el shell no se quede bloqueado esperando
            pid, status = os.waitpid(-1, os.WNOHANG)
            if pid == 0:
                break
    except ChildProcessError:
        pass

# Manejador para que Ctrl+C (SIGINT) no cierre el minishell
def sigint_handler(signum, frame):
    print("\nminishell> ", end="", flush=True)


def main():
    # Registro de señales antes de iniciar el loop
    signal.signal(signal.SIGCHLD, sigchld_handler)
    signal.signal(signal.SIGINT, sigint_handler)

    while True:
        try:
            entrada = input("minishell> ")

            if not entrada.strip():
                continue

            # shlex.split separa los argumentos respetando las comillas
            args = shlex.split(entrada)
            comando = args[0]

            if comando == "exit":
                break

            # Detectar ejecución en segundo plano
            bg = False
            if args[-1] == "&":
                bg = True
                args.pop()  # Se elimina el '&' para no pasarlo a execvp

            if not args:
                continue

            pid = os.fork()

            if pid < 0:
                print("Error: fork falló")

            elif pid == 0:
                # "Código del hijo"
                # Restaurar el comportamiento por defecto de Ctrl+C en el proceso hijo
                signal.signal(signal.SIGINT, signal.SIG_DFL)
                try:
                    os.execvp(comando, args)
                except FileNotFoundError:
                    print(f"minishell: {comando}: no se encontró el comando")
                    sys.exit(1)
            else:
                # "Código del padre"
                if not bg:
                    # Esperar al hijo si no es background
                    try:
                        os.waitpid(pid, 0)
                    except ChildProcessError:
                        pass
                # Si es background (bg == True), el padre continúa inmediatamente

        except EOFError:
            # Salida limpia con Ctrl+D
            print()
            break


if __name__ == "__main__":
    main()