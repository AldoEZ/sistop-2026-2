import os
import sys
import signal

#Función que ayuda a reconocer el símbolo "$"
#Es útil para reconocer variables de entorno en el comando ingresado
def expand_vars(args):
    result = []
    for arg in args:
        if arg.startswith("$"):
            var = arg[1:]
	    #Si encuentra una coincidencia, elimina el '$' y utiliza os.environ.get
	    #Esto nos ayuda a obtener el valor de la variable de entorno o manejar excepciones.
            result.append(os.environ.get(var, ""))
        else:
	    #Si no encuentra nada, simplemente avanza
            result.append(arg)
    return result

#Manejador de eventos sigchld, ayuda a evitar tener procesos zombies y manejar excepciones
def sigchld_handler(signum, frame):
    #Loop utilizado para recoger a todos los hijos terminados hasta que no quede ninguno
    while True:
        try:
	    #Recoge al hijo terminado sin bloquear
            pid, status = os.waitpid(-1, os.WNOHANG)
	    #El proceso se queda sin hijos
            if pid == 0:
                break
	#Si el proceso no tiene hijos se trabaja una excepción
        except ChildProcessError:
            break

#Sobreescribe el comportamiento original del handler de SIGCHLD
signal.signal(signal.SIGCHLD, sigchld_handler)

def main():
    while True:
        try:
            #Linea usada como prompt del shell
            cmd = input("turtle> ")
        except EOFError:
            break
	#Si no hay nada en el cmd, continúa con la ejecución del shell
        if not cmd.strip():
            continue
        #Manejador de salida del shell
        if cmd == "exit":
            break
        #Se rompen los argumentos para tokenizar casos muy específicos como el cd o el $
        args = cmd.split()
        #Manejo de $
        args = expand_vars(args)
        #Manejador de cd
        if args[0] == "cd":
            if len(args) == 1:
                print("No se especificó ninguna ruta")
            else:
                try:
                    #Si se especifica alguna ruta, se trata de ubicar y cambiar a dicha ruta
                    os.chdir(args[1])
                except OSError:
                    #Si no se encuentra, se maneja el error
                    print(f"No se encontró el directorio '{args[1]}'")
                continue
        #Crea un nuevo proceso con base en el actual
        pid = os.fork()
        #Proceso hijo
        if pid == 0:
            #Sobreescritura del handler SIGINT
            #Evita que mate el shell y mantenga el comportamiento del Ctrl+C regresando el default al hijo solamente
            signal.signal(signal.SIGINT, signal.SIG_DFL)
            try:
                #Reemplaza el proceso actual por el de args[0] y envia los argumentos restantes
                os.execvp(args[0], args)
            except FileNotFoundError:
                #Si no encuentra el comando, lanza un prompt
                print(f"Comando '{args[0]}' no encontrado")
                #Termina proceso hijo
                sys.exit(1)
        #Proceso padre
        else:  
            try:
                #Bloquea proceso padre
                #Espera a que el proceso hijo PID termine
                os.waitpid(pid, 0)
            #Manejador SIGINT Ctrl+C
            except KeyboardInterrupt:
                pass

if __name__ == "__main__":
    main()
