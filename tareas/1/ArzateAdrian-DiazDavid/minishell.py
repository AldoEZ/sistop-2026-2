import sys
import os
import shlex
import signal

# Conjunto para llevar el control de procesos hijos creados
children = set()

def sigchld_handler(signum, frame):
	"""
	Manejador de SIGCHLD
	Recolecta procesos hijos terminados sin bloquear al minishell
	para eviar procesos zombies.
	"""
	try:
		while True:
			pid, status = os.waitpid(-1, os.WNOHANG)
			if pid == 0:
				break
			children.discard(pid)
	except ChildProcessError:
		# No hay más hijos pendientes
		pass

def setup_signals():
	"""
	Configura las señales del shell:
	- SIGINT se ignora en el padre
	- SIGCHLD se maneja para recolectar hijos terminados
	"""
	signal.signal(signal.SIGINT, signal.SIG_IGN)
	signal.signal(signal.SIGCHLD, sigchld_handler)

def ejecutar_comando(args):
	"""
	Crea un proceso hijo y ejecuta el comando solicitado.
	El hijo ejecuta execvp() y el padre espera su finalización
	"""
	try:
		pid = os.fork()
	except OSError as e:
		print(f"minishell: error en fork(): {e}", file=sys.stderr)
		return
	
	if pid == 0:
		# Proceso hijo: restaura 'Ctrl + C' al comportamiento por defecto
		signal.signal(signal.SIGINT, signal.SIG_DFL)
	
		try:
			os.execvp(args[0], args)
		except FileNotFoundError:
			print(f"minishell: comando no encontrado: {args[0]}", file=sys.stderr)
		except PermissionError:
			print(f"minishell: permiso denegado: {args[0]}", file=sys.stderr)
		except Exception as e:
			print(f"minishell: error al ejecutar '{args[0]}':{e}", file=sys.stderr)
		
		os.exit(1)
	else: 
		# Proceso padre
		children.add(pid)
		
		try:
			while True:
				try:
					waited_pid, _ = os.waitpid(pid,0)
					if waited_pid == pid:
						children.discard(pid)
						break
				except InterruptedError:
					continue
				except ChildProcessError:
					# Ya fue recolectado por el manejador SIGCHLD
					children.dicard(pid)
					break
		except Exception as e:
			print(f"minishell: error esperando al hijo: {e}", file=sys.stderr)


def main():
	setup_signals()
	
	while True:
		try: 
			sys.stdout.write("minishel>>")
			sys.stdout.flush()
			
			lectura = sys.stdin.readline()
			
			if lectura == "":
				print("\nSaliendo de minishell...")
				break
			
			lectura = lectura.strip()
			if not lectura:
				continue
			
			try:
				args = shlex.split(lectura)
			except ValueError as e:
				print(f"minishell: error de sintaxis: {e}", file=sys.stderr)
				continue
			
			if not args:
				continue
			
			# Comando interno
			if args[0] == 'exit':
				print("Adios")
				break
			
			ejecutar_comando(args)
		except KeyboardInterrupt:
			# Como SIGINT está ignorada, esto es solo por robustez
			print()
			continue

		except Exception as e:
			print(f"minishell: error inesperado: {e}", file=sys.stderr)
		
	# Limpieza final de hijos pendientes
	for pid in list(children):
		try:
			os.waitpid(pid, 0)
		except ChildProcessError:
			pass

if __name__ == "__main__":
	main()
