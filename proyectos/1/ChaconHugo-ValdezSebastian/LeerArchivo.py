#@Autor(es):       Hugo Chacon, Sebastian Valdez
#@Fecha creacion:  16/05/2026
#@Descripcion:     micro sistema

import os
import struct

#Path al archivo que esta un directorio arriba
IMG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fiunamfs.img")

#4 sectores x 512 bytes = cluster
CLUSTER_SIZE = 2048  

#supernloque = cluster 0
def analizar_superbloque():
    with open(IMG_PATH, "rb") as f:
        # Se lee todo para despues hacer decode poco a poco
        superbloque = f.read(CLUSTER_SIZE)

        #0-4
        caracteres = superbloque[0:4].decode('ascii')
        print(f"0-4   ->  4 caracteres: {caracteres}") #se supone que no muestra nada

        #5-13
        fs_id = superbloque[5:13].decode('ascii')
        print(f"5-13  ->  Identificador: {fs_id}")
        if fs_id != "FiUnamFS":
            print("[ERROR] El sistema de archivos no es valido")
            return

        #14-18 version, debe ser 2026-2
        version = superbloque[14:18].decode('ascii')
        print(f"14-18 ->  Version: {version}")
        if version != "26-2":
            print("[ERROR] No es la version esperada")
            #return    #QUITAR EL RETURN COMENTADO---------------------------------------------------------------------------- 
            #Creo que el profe lo subio mal porque en el github lo modifico 2 dias antes de corregir el readme
            #y el readme antes estaba mal
            #------------------------------------------------------------------------------------------------------------

        #20-35
        etiqueta = superbloque[20:35].decode('ascii')
        print(f"20-35 ->  Etiqueta: {etiqueta}")
        
        #40-44
        cluster_bytes = struct.unpack('<I', superbloque[40:44])[0]
        print(f"Tamaño de cluster: {cluster_bytes} bytes")

        #50-54 
        dir_clusters = struct.unpack('<I', superbloque[50:54])[0]
        print(f"Clusters que mide el directorio: {dir_clusters}")

        #60-64 
        total_clusters = struct.unpack('<I', superbloque[60:64])[0]        
        print(f"Clusters que mide unidad completa: {total_clusters}")





if __name__ == "__main__":
    analizar_superbloque()
