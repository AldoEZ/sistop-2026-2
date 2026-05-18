#Tarea 2. Santa Claus
#Problema de sincronizción
#Autores: Brena de León Victor Javier, Cruz Manriquez Lizbeth

#Bibliotecas
import threading
import time
import random
import tkinter as tk

#Declaración de variables globales
num_elfos= 20
num_renos=9
elfos_esperando = []
renos_regresados = []
elfos_cont=0
renos_cont=0


#Uso de Mutex e Inicializacion de semáforos
mutex = threading.Lock()
santa_sem = threading.Semaphore(0)
elfos_sems = [threading.Semaphore(0) for i in range(num_elfos)]
renos_sems = [threading.Semaphore(0) for i in range(num_elfos)]
sem_label_elfos=threading.Semaphore(1)
sem_label_renos=threading.Semaphore(1)

#ya que e ejecucon sigue de manera infinita se añade esta linea.
stop_event = threading.Event()

#Listas para mensajes en la interfaz grafica
mensajes_elfos = []
mensajes_renos= []

#la funcion despliega una "notifiacion" o un label temporal
def notifiacion(frame_p,mensaje,color):
	#declara en lebale y sus atrubutos
	noti=tk.Label(frame_p,text=mensaje,font=("Arial",15), fg=color, padx=10, pady=10)
	noti.pack(fill="x", padx=5, pady=5, side="bottom")
	#despúes de 2 segundos de destruye
	noti.after(2000,noti.destroy)

#la funcion revisa si hay mensajes de los elfos
def revisar_mensajesE():
	global mensajes_elfos
	#si hay mensajes se realiza una notifiacion
	sem_label_elfos.acquire()
	if mensajes_elfos:
		mensaje=mensajes_elfos.pop()
		notifiacion(frames[0],mensaje,"blue")
	sem_label_elfos.release()
	ventana.after(300, revisar_mensajesE)

#la funcion revisa si hay mnesjaes de los renos
def revisar_mensajesR():
	global mensajes_renos
	#si hay mensajes se realiza una notifiacion
	sem_label_renos.acquire()
	if mensajes_renos:
		mensaje=mensajes_renos.pop()
		notifiacion(frames[1],mensaje,"violet")
	sem_label_renos.release()
	ventana.after(300, revisar_mensajesR)

#funcion para terminar nuestro programita
def cerrar_ventana():
	stop_event.set()
	ventana.destroy()

def contadores():
	label1=f"Elfos esperando {elfos_cont}/3"
	label2=f"Renos esperando {renos_cont}/9"

	cont_elfos.config(text=label1)
	cont_renos.config(text=label2)

	ventana.after(200,contadores)


#Declaración de la función Santa
def santa():
	global elfos_esperando, renos_regresados, num_renos, renos_cont,elfos_cont

	#cambio a:
	while not stop_event.is_set():
		santa_sem.acquire()

		with mutex:
			#si llegaron todos los renos
			if len(renos_regresados) >= num_renos:
				santa_label.config(text="Santa: ¡Es hora de repartir los regalos!", fg="green")
				time.sleep(2)
				santa_label.config(text="Santa: ¡Regalos repartidos!", fg="green")
				time.sleep(1)

				#time.sleep(2)

				#libera a los renos
				for i in range(num_renos):
					renos_regresados.pop(0)
					renos_sems[i].release()
					renos_cont-=1
				santa_label.config(text="Santa se vuelve a dormir",fg="red")
				time.sleep(1)

			#Ahora cuando tenenen problemas los elfos
			elif len(elfos_esperando) >= 3:
				santa_label.config(text="Santa: Ayudando a los elfos...", fg="cyan")
				time.sleep(1)

				elfos_atendidos = []
				for i in range(3):
					elfo_atendido = elfos_esperando.pop(0)
					elfos_atendidos.append(elfo_atendido)

				notifiacion(frames[2],f"Santa atendio a los elfos: {elfos_atendidos}","gray")
				time.sleep(1)

				#libera a los elfos
				for elfo_atendido in elfos_atendidos:
					elfos_sems[elfo_atendido].release()
					elfos_cont-=1

				santa_label.config(text="Santa se vuelve a dormir", fg="red")
				time.sleep(1)

#Declaración de la funcion elfo
def elfo(id):
	global elfos_esperando,elfos_cont

	#Sejecuta hasta un evento
	while not stop_event.is_set():
		time.sleep(random.randint(1,5))

		with mutex:
			#elfos que tienen problemas se almacenan
			if id not in elfos_esperando:
				elfos_esperando.append(id)
				elfos_cont+=1
			
			#se almacena el mensaje de mi elfo
			mensaje=f"Elfo {id} tiene un problema ({len(elfos_esperando)}/3)"
			mensajes_elfos.append(mensaje)
			
			#Si hay 3 elfos con problemas despiertan a santa
			if len(elfos_esperando) >= 3:
				santa_sem.release()

		#mi elfo se bloquea
		elfos_sems[id].acquire()

		notifiacion(frames[2], f"Elfo {id} recibió ayuda","gray")
		
#Declaración de la función reno
def reno(id):
	global renos_regresados, num_renos,renos_cont

	while not stop_event.is_set():
		time.sleep(random.randint(5,10))

		with mutex:
			#Se guarda los renos que van llegando
			if id not in renos_regresados:
				renos_regresados.append(id)
				renos_cont+=1
			
			#se comunica que mi reno llego
			mensaje=f"Reno {id} regresó ({len(renos_regresados)}/9)"
			mensajes_renos.append(mensaje)

			#Si ya llegaron los 9 renos se depierta a santa
			if len(renos_regresados) == num_renos:
				santa_label.config(text="Todos los renos despertaron a Santa", fg="green")
				time.sleep(1)
				santa_sem.release()

		#se bloquen mis renos
		renos_sems[id].acquire()

		notifiacion(frames[2], f"Reno {id} regresa de vaciones","gray")
			

#funcion principal
if __name__ == "__main__":
	#Se inicializa la interfaz grafica
	ventana = tk.Tk()
	ventana.title("Santa y la concurrencia")
	ventana.geometry("1500x900")

	#Se separa por frames mi interfaz
	frames=[]
	for i in range(3):
		f=tk.Frame(ventana, relief="flat")
		f.grid(row=3, column=i,sticky="nsew")
		ventana.columnconfigure(i,weight=1)
		frames.append(f)

	#Se destina un label para santa
	santa_label=tk.Label(ventana,text="Santa esta Dormido", font=("Arial",15,), fg="red")
	santa_label.grid(row=0, column=1, pady=20, padx=20)


	#Labels contadores
	cont_elfos=tk.Label(ventana,text=f"Elfos esperando {elfos_cont}/3", font=("Arial",15,), fg="red")
	cont_elfos.grid(row=0, column=0, pady=20, padx=20)
	cont_renos=tk.Label(ventana,text=f"Renos esperando {renos_cont}/9", font=("Arial",15,), fg="red")
	cont_renos.grid(row=0, column=2, pady=20, padx=20)

	#Crear hilo de santa
	threading.Thread(target=santa, daemon=True).start()

	#Se sabe que hay n cantidad de elfos
	for i in range(num_elfos):
		threading.Thread(target=elfo, args=(i,), daemon=True).start()

	#Se crean renos
	for i in range(num_renos):
		threading.Thread(target=reno, args=(i,), daemon=True).start()

	#revisa los mensajes de los elfos
	threading.Thread(target=revisar_mensajesE, daemon=True).start()

	#revisa los mensajes de los renos
	threading.Thread(target=revisar_mensajesR, daemon=True).start()

	threading.Thread(target=contadores, daemon=True).start()

	#si ce cierra la ventana se termina el programita
	ventana.protocol("WM_DELETE_WINDOW", cerrar_ventana)
	ventana.mainloop()