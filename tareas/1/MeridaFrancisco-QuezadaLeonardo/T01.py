import os
import signal 
import time
import shlex
import time

#--------------------------------------------------------------------------------------------------------------------
#Manejadores de señales

#Manejador de señales de procesos hijos
def sigchld_handler(signum, frame):
	try:
		#El ciclo while permite recuperar todos los procesos hijos que terminen bajo la misma señal "SIGCHLD"
		while True:
			pid, status = os.waitpid(-1,os.WNOHANG)
			#Si ya no hay procesos hijos terminados, se rompe el ciclo 
			if pid == 0:
				break


			#Descomentar para ver que sí sirve Ctrl + C en los procesos hijos
			#print('Termino el proceso hijo')


	except ChildProcessError:
		pass

#--------------------------------------------------------------------------------------------------------------------


def main():

#Manejo de señales
	signal.signal(signal.SIGCHLD, sigchld_handler) #Llama al manejador de señales de procesos hijos
	signal.signal(signal.SIGINT, signal.SIG_IGN) #Se ignora la señal "SIGINT" para el proceos padre

#Loop principal del shell
	while True:
		#-------------------------------------------------
		#Dado que el proceso padre no espear a que el hijo termine su ejecución para imprimir de nuevo el prompt, se durme 
		#proceso padre por 0.01 segundos para que se tega una impresión más limpia.

		time.sleep(0.01)

		#-------------------------------------------------

		##Imprimir pormpt.
		
		prompt = input("miniShell🏀>: ")
		

		##Parsear argumentos
		try: 
			args = shlex.split(prompt)

		except ValueError:
			print('Error al ingresar el comando. Cierre comillas por favor')
			args = []
			continue


		#Si no se ingreso ningun comando, entonces se ignora el resto del ciclo dado que args[0] daría error
		if not prompt:
			continue

		##Salir del programa
		if args[0] == 'exit':
			break

#Creación y ejecución de proceso hijo
#--------------------------------------------------------------------------------------------------------------------
		#Creamos un proceso hijo
		pid = os.fork()

		if pid < 0: 
			print('Error al hacer la partición del proceso')
		elif pid == 0:
			#Proceso hijo.

			signal.signal(signal.SIGINT, signal.SIG_DFL) #Se reestablece la señal SIGINT para el proceso hijo

			try:
				##Se manda args[0] como comando a ejecutar y el resto de args como parámetros. 
				os.execvp(args[0],args)
			except FileNotFoundError:
				print(f'{args[0]} no pudo ser encontrado')
			except OSError as e:
				##Cualquier otro error
				print(f'No se pudo ejecutar {args[0]}: {e}')
			
			os._exit(1) 

		else:
			#Proceso padre
			pass
#--------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
	main()
