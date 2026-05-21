"""
Proyecto (Micro) sistema de archivos multihiloss
Autores: 
    - Gonzalez Falcon Luis Adrían
    - Lopez Morales Fernando Samuel
Entrega 2026-05-21
"""

import threading
import time
import sys
from fiunamfs import FiUnamFS


orden_actual = {"comando": None, "argumentos": []}
sistema_corriendo = True

#mutex para proteger el disco
mutex_fs = threading.Semaphore(1)

#semaforos sincronización
sem_orden_pendiente = threading.Semaphore(0)
sem_orden_terminada = threading.Semaphore(0)


#Hilo secundario que actúa cuando sucede algún evento
def hilo_trabajador(motor_fs):
    global sistema_corriendo, orden_actual
    
    #print("\nHilo TRABAJADOR iniciado y esperando...")
    
    while sistema_corriendo:
        
        #Hilo trabajador adquiere se queda en espera hasta que la interfaz suelte el mutex.
        sem_orden_pendiente.acquire()
        
        if not sistema_corriendo:
            print("Hilo TRABAJADOR saliendo")
            break
        
        print("Hilo TRABAJADOR despierta")
        comando = orden_actual["comando"]
        args = orden_actual["argumentos"]
        
        # Hilo bloquea el disco para realizar una exclusión
        print("Hilo TRABAJADOR adquiere el mutex del disco para que nadie más lo use")
        mutex_fs.acquire()
        
        try:
            print(f"Hilo TRABAJADOR ejecuta el comando {comando.upper()}")
            time.sleep(0.5)             

            # Lista de acciones que puede realizar el hilo.
            if comando == "listar":
                motor_fs.listar_directorio()
            elif comando == "extraer":
                motor_fs.copiar_al_exterior(args[0], args[1])
            elif comando == "insertar":
                motor_fs.copiar_al_interior(args[0], args[1])
            elif comando == "eliminar":
                motor_fs.eliminar_archivo(args[0])

        except Exception as e:
            print(f"Hilo TRABAJADOR sufrió un error {e}")
        finally:
            #Se libera el disco del mutex que generab exclusión
            print("Hilo TRABAJADOR libera el mutex del disco.")
            mutex_fs.release()
        
        # Le avisamos a la interfaz que ya terminamos el trabajo
        print("Hilo TRABAJADOR vuelve a quedar en modo espera")
        sem_orden_terminada.release()


#Hilo principal que va a contener la funcionalidad de la interfaz
def main():
    global sistema_corriendo, orden_actual
    
    print("========= INICIANDO PROYECTO 1 =========")
    
    #trycatch por si hay un dato que no es válido
    try:
        motor = FiUnamFS("./fiunamfs.img")
        motor.conectar()
        motor.validar_superbloque()
    except Exception as e:
        print(f"Error al iniciar: {e}")
        return

    # 2. Arrancar el hilo trabajador concurrente
    trabajador = threading.Thread(target=hilo_trabajador, args=(motor,))
    trabajador.start()
    time.sleep(0.2)
    
    #Menú del proyecto 
    while sistema_corriendo:
        print("\n\nMENÚ PROYECTO 1 SISTEMAS OPERATIVOS\n\n")
        print("1. Listar contenido del directorio")
        print("2. Copiar archivo de FiUnamFS a tu sistema (Extraer)")
        print("3. Copiar archivo de tu sistema a FiUnamFS (Insertar)")
        print("4. Eliminar un archivo del FiUnamFS")
        print("5. Salir")
        
        opcion = input("Opción: ")
        

        #Estructuras de control que determinan el flujo respecto a la decisión del usuario
        if opcion == "1": #Listar contenido del directorio
            orden_actual["comando"] = "listar"
            orden_actual["argumentos"] = []
            
            print("Hilo INTERFAZ para listar elementos")
            sem_orden_pendiente.release()
            sem_orden_terminada.acquire()
            
        elif opcion == "2": #Copiar archivo de FiUnamFS a tu sistema (Extraer)
            #Necesitamos el nombre del archivo dentro de la imagen y también el nombre con el que lo copiaremos al disco
            archivo_origen = input("Nombre del archivo EXACTO en FiUnamFS (con extensión): ")
            archivo_destino = input("Nombre con el que se guardará en tu PC (con extensión): ")
            
            orden_actual["comando"] = "extraer"
            orden_actual["argumentos"] = [archivo_origen, archivo_destino]
            
            print(f"Hilo INTERFAZ para extraer el archivo {archivo_origen}")
            sem_orden_pendiente.release()
            sem_orden_terminada.acquire()
            
        elif opcion == "3": #Copiar archivo de PC a FIUnamFS (Insertar)
            #Se necesita el nombre del archivo dentro de PC y también el nombre ocn el que se guardará
            archivo_origen = input("Ruta del archivo en tu PC (debe tener la extensión): ")
            archivo_destino = input("Nombre que tendrá dentro de FiUnamFS (con extensión): ")
            
            orden_actual["comando"] = "insertar"
            orden_actual["argumentos"] = [archivo_origen, archivo_destino]
            
            print(f"Hilo INTERFAZ para insertar el archivo {archivo_origen}")
            sem_orden_pendiente.release()
            sem_orden_terminada.acquire()
            
        elif opcion == "4": # Eliminar un archivo del FiUnamFS
            # SOlo necesitamos el nombre del archivo a borra dentro del disco
            archivo_a_borrar = input("Nombre del archivo a borrar: ")
            orden_actual["comando"] = "eliminar"
            orden_actual["argumentos"] = [archivo_a_borrar]
            
            print(f"Hilo INTERFAZ para borrar el archivo: {archivo_a_borrar}")
            sem_orden_pendiente.release()
            sem_orden_terminada.acquire()
            
        
        elif opcion == "5": # Salir
            print("Hilo INTERFAZ, saliendo")
            sistema_corriendo = False
            sem_orden_pendiente.release() 
            trabajador.join() 
            motor.desconectar()
            break
        else:
            print("Opción inválida. Intenta de nuevo (1-5)\n")

if __name__ == "__main__":
    main()