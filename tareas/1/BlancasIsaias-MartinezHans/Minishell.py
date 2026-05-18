import os #para llamar al sistema (fork, exec, wait)
import signal #para manejar señales (SIGINT, SIGCHLD)
import sys #para entrada/salida estandar
import shlex #para separar "ls -l /etc" en ['ls', '-l', '/etc']

def sigchld_handler(signum, frame):

    #manejador asincrono para SIGCHLD, evitar al hijo zombie
    try:
        while True:
            #WNOHANG: no bloquea al padre si el hijo no ha terminado
            #nos devuelve (0,0) si no hay cambios, o el (PID,status) del hijo.
            pid, status = os.waitpid(-1, os.WNOHANG)
            if pid <= 0:
                break
    except ChildProcessError:
        #no hay mas procesos hijos para esperar
        pass

def setup_signals():
    #para configurar el comportamiento inicial de las señales
    #el shell padre ignora ctrl+c para no cerrarse
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    #registramos el manejador para limpiar hijos que ya terminaron
    signal.signal(signal.SIGCHLD, sigchld_handler)


def ejecutar_comando(args):
    #crear un proceso hijo y ejecutar el programa solicitado
    pid = os.fork() #CLONACION

    if pid < 0:
        print("Error: Fallo al realizar fork.")
    
    elif pid == 0:
        #PROCESO HIJO
        #el hijo debe responder a ctrl+c
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        
        try:
            #reemplazamos al hijo con el comando solicitado
            os.execvp(args[0], args)
        except FileNotFoundError:
            print(f"Minishell: comando no encontrado: {args[0]}")
            os._exit(1) #terminamos al hijo si falla el comando
        except Exception as e:
            print(f"Minishell: error al ejecutar: {e}")
            os._exit(1)
            
    else:
        #el padre no espera aqui con wait() porque lo hace asincronamente
        #mediante la señal SIGCHLD configurada arriba
        pass


def main():
    setup_signals()
    
    while True:
        try:
            #mostrar prompt y leer entrada
            sys.stdout.write("Minishell> ")
            sys.stdout.flush()
            
            linea = sys.stdin.readline()
            
            #manejar EOF (ctrl+d) para salir limpios
            if not linea:
                print("\nSaliendo...")
                break
            
            #separar el comando y sus argumentos
            args = shlex.split(linea)
            if not args:
                continue
            
            #comando interno: exit
            if args[0] == "exit":
                print("Adiós!")
                break
                
            #ejecutar comando externo
            ejecutar_comando(args)
            
        except KeyboardInterrupt:
            #usa ctrl+c mientras se escribe en el prompt
            print("\nUsa 'exit' para salir.")
            continue

if __name__ == "__main__":
    main()