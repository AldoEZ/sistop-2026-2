#!/usr/bin/python3

#Programa encargado de realizar operaciones sobre el disco entero
#Autores: Isaac Campos, Alejandro Martinez
#Fecha de realización: 18 Mayo 2026

from superbloque import SuperBloque
from entrada import EntradaDir
import herramientas as h

#Hay que investigar la manera de declarar las consrantes una vez para todos los archivos
TAM_ENTRADA_DIR = 64
ARCHIVO_VACIO = '/'

#Falta documentar todoooo q flojera ya me quiero dormir

class Disco:
    def __init__(self,ruta_img):
        self.ruta_img = ruta_img
        self.superbloque = SuperBloque(self.ruta_img)
        self.cargarDirectorio()
    
    def cargarDirectorio(self):
        with open(self.ruta_img, 'rb') as img:
            img.seek(self.superbloque.desp_dir)
            datos = img.read(self.superbloque.tam_dir)
        
        self.entradas = []
        for i in range(0, len(datos), TAM_ENTRADA_DIR):
            pedazo_entrada = datos[i:i+TAM_ENTRADA_DIR]
            entrada = EntradaDir(pedazo_entrada)
            self.entradas.append(entrada)
    
    def listarEntradas(self):
        for entrada in self.entradas:
            if entrada.tipo_archivo != '/':
                print(entrada)
    
    def encontrarEntrada(self,nombre):
        for entrada in self.entradas:
            if entrada.nombre_archivo.strip('\x00').strip() == nombre:
                return entrada
        return None
    
    def leerEntrada(self,nombre):
        entrada = self.encontrarEntrada(nombre)
        if entrada != None:
            offset_entrada = entrada.cluster_incial * self.superbloque.tam_cluster
            with open(self.ruta_img, 'rb') as img:
                img.seek(offset_entrada)
                datos = img.read(entrada.tam_archivo)
                return datos
        else:
            print(f"No se encontró la entrada")
            return None
    
    def escribirEntrada(self, nombre, datos):

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
        self.actualizarDisco()
        return True


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
    
    def eliminarEntrada(self,nombre):
        entrada = self.encontrarEntrada(nombre)
        if entrada != None:
            entrada.eliminar()
            self.actualizarDisco()
        else:
            print(f"No se encontró la entrada")
    
    def actualizarDisco(self):
        with open(self.ruta_img, 'r+b') as img:
            img.seek(self.superbloque.desp_dir)
            salida = bytearray()
            for entrada in self.entradas:
                salida.extend(entrada.pasarBytes())
            salida = salida[:self.superbloque.tam_dir].ljust(self.superbloque.tam_dir, b'\x00')
            img.write(salida)


#Pruebas para comprobar que todo funciona

if __name__ == '__main__':
    disco = Disco('../fiunamfs.img')

    # Prueba 1: listar
    print("=== Archivos en el disco ===")
    disco.listarEntradas()

    # Prueba 2: buscar un archivo que exista (usa un nombre que viste en prueba 1)
    nombre = "README.org"    # cambia esto por un nombre real que apareció arriba
    print(f"\n=== Buscar '{nombre}' ===")
    entrada = disco.encontrarEntrada(nombre)
    if entrada:
        print(f"Encontrado: {entrada.nombre_archivo}, tamaño: {entrada.tam_archivo}")
    else:
        print("No encontrado")

    # Prueba 3: leer ese archivo
    print(f"\n=== Leer '{nombre}' ===")
    datos = disco.leerEntrada(nombre)
    if datos:
        print(f"Leídos {len(datos)} bytes")
        print(f"Primeros 50 bytes: {datos[:50]}")

    # Prueba 4: escribir un archivo nuevo
    print("\n=== Escribir 'nuevo.txt' ===")
    contenido = b"Hola FiUnamFS desde Python"
    disco.escribirEntrada("nuevo.txt", contenido)
    print("Escrito, verificando con listar:")
    disco.listarEntradas()

    # Prueba 5: eliminar el archivo recién creado
    print("\n=== Eliminar 'nuevo.txt' ===")
    disco.eliminarEntrada("nuevo.txt")
    print("Eliminado, verificando con listar:")
    disco.listarEntradas()