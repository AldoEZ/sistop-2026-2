#!/usr/bin/python3

#Programa encargado de realizar operaciones sobre el disco entero
#Autores: Isaac Campos, Alejandro Martinez
#Fecha de realización: 18 Mayo 2026

from .superbloque import SuperBloque
from .entrada import EntradaDir
from . import herramientas as h 
import threading

#Hay que investigar la manera de declarar las consrantes una vez para todos los archivos
TAM_ENTRADA_DIR = 64
ARCHIVO_VACIO = '/'


#Se define la clase para el disco

class Disco:

    def __init__(self,ruta_img):
        self.ruta_img = ruta_img
        self.superbloque = SuperBloque(self.ruta_img)
        self.cargarDirectorio()
        self.lock = threading.RLock()
        self.condicion = threading.Condition(self.lock)
        self.operaciones = []
        self.hilo = threading.Thread(
        target=self.hiloEscritura,daemon=True)
        self.hilo.start()

    #Lee todos los datos después del superbloque, después itera por cada una y las agrega a una lista
    
    def cargarDirectorio(self):
        with open(self.ruta_img, 'rb') as img:
            img.seek(self.superbloque.desp_dir)
            datos = img.read(self.superbloque.tam_dir)
        
        self.entradas = []
        for i in range(0, len(datos), TAM_ENTRADA_DIR):
            pedazo_entrada = datos[i:i+TAM_ENTRADA_DIR]
            entrada = EntradaDir(pedazo_entrada)
            self.entradas.append(entrada)
    
    #Lista las entradas que no están vacías

    def listarEntradas(self):
        no_vacias = []
        for entrada in self.entradas:
            if entrada.tipo_archivo != '/':
                no_vacias.append(entrada.nombre_archivo.strip())
        return no_vacias
    
    #Busca una entrada por su nombre, se modifica para no incluir los espacios en blanco de los bytes completos del nombre

    def encontrarEntrada(self,nombre):
        for entrada in self.entradas:
            if entrada.nombre_archivo.strip('\x00').strip() == nombre:
                return entrada
        return None

    #Busca la entrada y si la encuentra carga todos los datos en bruto
    
    def leerEntrada(self,nombre):
        entrada = self.encontrarEntrada(nombre)
        if entrada != None:
            offset_entrada = entrada.cluster_incial * self.superbloque.tam_cluster
            with open(self.ruta_img, 'rb') as img:
                img.seek(offset_entrada)
                datos = img.read(entrada.tam_archivo)
                return datos
        else:
            return None

    #Se asegura que no haya una archivo con el mismo nombre, después busca si hay espacio suficiente seguido
    #para escribir los datos solicitados, después intenta escribir una entrada al directorio. Finalmente actualiza el disco
    
    def escribirEntrada(self, nombre, datos):

        with self.lock:

            if self.encontrarEntrada(nombre) is not None:
                print(f"Ya existe un archivo con el nombre '{nombre}'")
                return False
        
            clusters = (len(datos) + self.superbloque.tam_cluster - 1) // self.superbloque.tam_cluster
            cluster_incio = self.encontrarEspacio(clusters)
            if cluster_incio is None:
                print(f"No se encontró suficiente espacio en disco")
                return False

            else: 
                with open(self.ruta_img, 'r+b') as img:
                    img.seek(cluster_incio * self.superbloque.tam_cluster)
                    img.write(datos)
            
            entrada_libre = None
            for entrada in self.entradas:
                if entrada.tipo_archivo == ARCHIVO_VACIO:
                    entrada_libre = entrada
                    break
                
            if entrada_libre is None:
                print(f"No hay entradas libres en el directorio")
                return False
            
            entrada_libre.crearNuevo(nombre, len(datos), cluster_incio)
            with self.condicion:
                self.operaciones.append("sync")
                self.condicion.notify()
            return True

    #Se encarga de encontrar el espacio seguido necesario para escribir el archivo

    def encontrarEspacio(self, clusters_necesarios):
        ocupados = []
        for entrada in self.entradas:
            if entrada.tipo_archivo != ARCHIVO_VACIO and entrada.tam_archivo > 0:
                n_clusters = (entrada.tam_archivo + self.superbloque.tam_cluster - 1) // self.superbloque.tam_cluster
                ocupados.append(entrada.cluster_incial + n_clusters)

        if not ocupados:
            return self.superbloque.desp_datos // self.superbloque.tam_cluster
        
        siguiente = max(ocupados)
        
        if siguiente + clusters_necesarios > self.superbloque.num_clusters_tot:
            return None
        
        return siguiente
    
    #Encuentra el archivo y llama a su eliminación, después actualiza el disco

    def eliminarEntrada(self,nombre):
        with self.lock:
            entrada = self.encontrarEntrada(nombre)
            if entrada != None:
                entrada.eliminar()
                with self.condicion:
                    self.operaciones.append("sync")
                    self.condicion.notify()
            else:
                print(f"No se encontró la entrada")

    #Lee todo y lo reescribe
    
    def actualizarDisco(self):
        with self.lock:
            with open(self.ruta_img, 'r+b') as img:
                img.seek(self.superbloque.desp_dir)
                salida = bytearray()
                for entrada in self.entradas:
                    salida.extend(entrada.pasarBytes())
                salida = salida[:self.superbloque.tam_dir].ljust(self.superbloque.tam_dir, b'\x00')
                img.write(salida)

  
    def sobrescribirEntrada(self, nombre, datos):
        with self.lock:
            entrada = self.encontrarEntrada(nombre)
            if entrada is None:
                return False
            with open(self.ruta_img, 'r+b') as img:
                offset = entrada.cluster_incial * self.superbloque.tam_cluster
                img.seek(offset)
                img.write(datos)
            entrada.tam_archivo = len(datos)
            with self.condicion:
                self.operaciones.append("sync")
                self.condicion.notify()
            return True


    def hiloEscritura(self):

        while True:

            with self.condicion:

                while not self.operaciones:
                    self.condicion.wait()

                operacion = self.operaciones.pop(0)

            if operacion == "sync":
                self.actualizarDisco()
