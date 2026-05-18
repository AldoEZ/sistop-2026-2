import os
import signal
import sys
import time
import shlex
import readline

# Argumentos para signal.signal
# SIG_DFL -> Realiza la función predeterminada para una señal. Para SIGCHLD es ignorar
# SIG_IGN -> Manejador de señales estándar: ignora la señal dada    
# SIGCHLD -> El proceso hijo se detuvo o terminó
# SIGINT -> Interrumpe desde el teclado (CTRL + C)


def handler(signum, frame):
    try:
        while True:
            #Atrapa cualquier excepción
            pid, status = os.waitpid(-1, os.WNOHANG)
            if pid == 0:
                break
    #No tenemos nada que procesar
    except ChildProcessError:
        pass
        

def run(args):
    
    try:
        #Clonación del programa en padre e hijo y obtenemos sus ids
        id = os.fork()
    except OSError as e:
        print("Algo salió mal: ", e)
        return
    
    #Bloque ejecutable únicamente por el hijo
    if(id == 0):

        #Restablecemos la interrupción del proceso (CTRL + C)
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        
        try:
            #Ejecutamos los argumentos
            os.execvp(args[0], args)
        except FileNotFoundError:
            print(f"{args[0]}: comando no encontrado D:", file=sys.stderr)
            os._exit(127)
        except OSError as e:
            print(f"error: {e}", file=sys.stderr)
            exit(1)
        # Atrapa cualquier otro error inesperado
        except Exception as e:
            print(f"error inesperado: {e}", file=sys.stderr)
            os._exit(1)
    else:
        #Agregamos un pequeño retraso para que no se sobreponga el texto del minishell con el del hijo
        time.sleep(0.03)


def main():

    #Shell padre ignora CTRL + C
    signal.signal(signal.SIGINT, signal.SIG_IGN) 
    
    #Manejo de SIGCHLD de forma asincrona
    signal.signal(signal.SIGCHLD, handler) 
    
    #Ejecución del bucle infinito para recibir argumentos en el minishell
    while(True):
        
        try:
            entrada = input("minishell> ")
            if not entrada.strip():
                continue 
            
            if(entrada=='exit'):
                os._exit(0)

            #Almacenamos todos los argumentos en una lista y los procesamos
            args=shlex.split(entrada)
            run(args)
        except EOFError:
            print('exit')
            break
        except ValueError as e:
            print(e)
            continue


if __name__ == "__main__":
    main()
