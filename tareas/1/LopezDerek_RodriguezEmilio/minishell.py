import os # Permite usar llamadas al sistema como fork(), execvp(), waitpid()
import signal
import sys
import shlex

def sigchld_handler(signum, frame):
  try:
     while True:
      pid, status = os.waitpid(-1, os.WNOHANG)
       # -1 -> "cualquier proceso hijo"
      if pid == 0: #Si pid es 0, no hay hijos terminados
                break
      print(f"[Proceso hijo {pid} terminado]")
  except ChildProcessError: #Excepcion para cuando no haya procesos hijos
        pass

def setup_signals():
    signal.signal(signal.SIGINT, signal.SIG_IGN) #El comando Crtl+C no afecta

    # Solo instalar SIGCHLD si el sistema lo soporta
    if hasattr(signal, "SIGCHLD"):
        signal.signal(signal.SIGCHLD, sigchld_handler)

def execute_command(command):
   try:

        # fork() crea un nuevo proceso hijo
        pid = os.fork()
   # Manejo de error si fork falla
   except OSError as e:
        print(f"Error al crear proceso: {e}")
        return

   if pid == 0:
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        try:
          os.execvp(command[0], command)

        except FileNotFoundError:
            print("Comando no encontrado")
        except Exception as e:
            print(f"Error al ejecutar: {e}")
        os._exit(1)
   else:
    pass

def main():

    # Configurar señales del shell
    setup_signals()

    while True:

        try:
          line = input("minishell> ")# Mostrar el prompt y esperar entrada del usuario

          # Si el usuario solo presiona ENTER se ignora
          if not line.strip():
                continue
          args = shlex.split(line)
          if args[0] == "exit":
                print("Saliendo de minishell...")
                sys.exit(0)
          execute_command(args)
        except EOFError:
            print("\nSaliendo...")
            break
        except Exception as e:
            print("Error:", e)
if __name__ == "__main__":
    main()


