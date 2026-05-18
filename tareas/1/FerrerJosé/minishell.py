# autor
# Ferrer Cordero José Mauel
import os
import signal
import shlex
import sys

# Conjunto para registrar los procesos hijos activos
children = set()


def sigchld_handler(signum, frame):
    """
    Manejador de SIGCHLD.
    Recolecta procesos hijos terminados sin bloquear para evitar zombies.
    """
    try:
        while True:
            pid, status = os.waitpid(-1, os.WNOHANG)
            if pid == 0:
                break

            children.discard(pid)

            if os.WIFEXITED(status):
                exit_code = os.WEXITSTATUS(status)
                print(f"\n[Proceso {pid} terminó con código {exit_code}]")
            elif os.WIFSIGNALED(status):
                sig = os.WTERMSIG(status)
                print(f"\n[Proceso {pid} terminó por señal {sig}]")
    except ChildProcessError:
        # No hay más hijos para recolectar
        pass


def ignore_sigint(signum, frame):
    """
    El shell padre ignora Ctrl+C para no terminar su ejecución.
    """
    print()


def main():
    # Instalar manejadores de señales
    signal.signal(signal.SIGCHLD, sigchld_handler)
    signal.signal(signal.SIGINT, ignore_sigint)

    while True:
        try:
            line = input("minishell> ")
        except EOFError:
            print("\nSaliendo de minishell...")
            break
        except KeyboardInterrupt:
            print()
            continue

        line = line.strip()

        if not line:
            continue

        if line == "exit":
            print("Saliendo de minishell...")
            break

        try:
            args = shlex.split(line)
        except ValueError as e:
            print(f"Error al interpretar la línea: {e}", file=sys.stderr)
            continue

        if not args:
            continue

        try:
            pid = os.fork()
        except OSError as e:
            print(f"Error al crear el proceso hijo: {e}", file=sys.stderr)
            continue

        if pid == 0:
            # Proceso hijo:
            # Restaurar comportamiento por defecto de SIGINT
            signal.signal(signal.SIGINT, signal.SIG_DFL)

            try:
                os.execvp(args[0], args)
            except FileNotFoundError:
                print(f"Comando no encontrado: {args[0]}", file=sys.stderr)
            except PermissionError:
                print(f"Permiso denegado: {args[0]}", file=sys.stderr)
            except Exception as e:
                print(f"Error al ejecutar el comando: {e}", file=sys.stderr)

            # Si execvp falla, el hijo debe terminar
            os._exit(1)

        else:
            # Proceso padre:
            children.add(pid)

            # Espera a que el hijo actual termine, pero la recolección
            # real ocurre en el manejador de SIGCHLD
            while pid in children:
                signal.pause()


if __name__ == "__main__":
    main()