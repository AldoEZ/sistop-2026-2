import os
import signal #Permite manejar señales del SO, como SIGCHLD o SIGINT
import shlex #Se usa para dividir comandos en argumentos, es como split() pero para todo el comando no solo para la cadena de caracteres
import sys # Se utiliza para exit() el cual termina el programa

# ------------------------------
# Manejador de procesos hijos
# ------------------------------
def sigchld_handler(signum, frame): #número de señal, estado actual del programa
    try:
        while True:
            pid, status = os.waitpid(-1, os.WNOHANG) #Captura el proceso hijo, sin bloquear el programa para que shell siga funcionando. Esto evita procesos zoombie
            if pid == 0:
                break
            print(f"\n[Proceso {pid} terminado]")
    except ChildProcessError:
        pass


# ------------------------------
# Ignorar Ctrl+C en el shell
# ------------------------------
def sigint_handler(signum, frame):
    print()


# instalar manejadores de señal
signal.signal(signal.SIGCHLD, sigchld_handler)
signal.signal(signal.SIGINT, sigint_handler) #Captura cuando el usuario mande un ctrl+c


# ------------------------------
# Bucle principal del shell
# ------------------------------
while True:
    try:
        comando = input("minishell> ")

        if not comando.strip():
            continue

        args = shlex.split(comando)

        # Si el usuario escribe exit para salir se separa con split y se agrega una linea de saliendo...
        #Esto permite que se termine el shell limpiamente
        if args[0] == "exit":
            print("Saliendo del minishell...")
            sys.exit(0)

        # se crea proceso hijo con el fork, esto hace que se divida el proceso en 2, el padre que sigue siendo el shell y el hijo que va a ejecutar el comando
        # para que posteriormente se muera cuando acabe de ejecutarse o el usuario haga un ctrl c
        try:
            pid = os.fork()
        except OSError: #Si no se puede crear el fork manda este mensaje de retorno
            print("Error: no se pudo crear el proceso")
            continue
        
        if pid == 0:

            # en caso de que "al hijo" mientras se esta ejecutando le llega un ctrl+c que terminaría el proceso sí lo termina ya que es al hijo al que mata no al padre
            #Este es el comportamiento "predeterminado" para esta señal
            signal.signal(signal.SIGINT, signal.SIG_DFL)

            try:
                os.execvp(args[0], args)
            except FileNotFoundError: # Aqui si el programa no reconoce el comando, mandamos al minishell el print de que no se encontró
                print("Comando no encontrado")
                os._exit(1)

        else:
            pass

    except EOFError: #En caso de un Ctrl + D
        print("\nSaliendo del minishell...")
        break