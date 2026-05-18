#!/usr/bin/python3

#Programa encargado de leer el superbloque de la imagen proporcionada
#Autores: Isaac Campos, Alejandro Martinez
#Fecha de realización: 15 Mayo 2026

import herramientas as h

#Constantes del sistema de archivos mencionados en el planteamiento

NOM_FS = "FiUnamFS"
VER_FS = "24-2"

TAM_SECTOR = 512
NUM_SECT_CLUSTER = 4
TAM_CLUSTER = TAM_SECTOR * NUM_SECT_CLUSTER

#Anoté esto de los requerimientos pero como se calcula la mayoría quizá no sea necesario...
CLUSTER_INI_DIR = 1
CLUSTER_FIN_DIR = 8
NUM_CLUSTER_DIR = 7
TAM_ENTRADA_DIR = 64

#Se define la clase para el superbloque
class SuperBloque:
    def __init__(self, ruta_img):
        self.ruta_img = ruta_img
        self.leerSuperbloque()

#No tengo idea por qué lee 24-2 en lugar de 26-2? Enviar correo al profe y preguntar el martes, por ahora cambiar requerimiento a 24-2
        
    def leerSuperbloque(self):
        with open(self.ruta_img,'rb') as bin_img:
            #Aquí se lee el primer cluster, se va leyenfo campo por campo y después se calculan los valores para el directorio
            sp_bloque = bin_img.read(TAM_CLUSTER)

            self.nombre = sp_bloque[5:14].decode('ascii').strip('\x00')
            self.version = sp_bloque[14:19].decode('ascii').strip('\x00')
            self.etiqueta = sp_bloque[20:36].decode('ascii').strip('\x00')

            self.tam_cluster = h.leerLe(sp_bloque[40:44])
            self.num_clusters_dir = h.leerLe(sp_bloque[50:54])
            self.num_clusters_tot = h.leerLe(sp_bloque[60:64])

            self.desp_dir = CLUSTER_INI_DIR * self.tam_cluster
            self.tam_dir = self.num_clusters_dir * self.tam_cluster
            self.desp_datos = (CLUSTER_INI_DIR + self.num_clusters_dir)*self.tam_cluster

            #Se verifica que se cumpla con nombre y versión
            if self.nombre != NOM_FS:
                raise RuntimeError(f"Nombre incorrecto: encontré '{self.nombre}' esperaba '{NOM_FS}'")
            if self.version != VER_FS:
                raise RuntimeError(f"Verión incorrecta: encontré '{self.version}' esperaba '{VER_FS}'")
            

#Main para probar que todo se lee bien
"""
if __name__ == '__main__':
    sb = SuperBloque('../fiunamfs.img')
    print(sb.nombre)
    print(sb.version)
    print(sb.etiqueta)
    print(sb.tam_cluster)
    print(sb.num_clusters_dir)
    print(sb.num_clusters_tot)
    print(sb.desp_dir)
    print(sb.desp_datos)
"""
