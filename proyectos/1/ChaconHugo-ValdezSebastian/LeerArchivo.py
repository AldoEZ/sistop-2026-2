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
            print("Pero se continua porque asi dijo el profe")
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



def listar_directorio():
    ENTRY_SIZE = 64
    START_OFFSET = 1 * CLUSTER_SIZE  #empieza en 1 porque superbloque es 0
    DIR_SIZE = 8 * CLUSTER_SIZE      #directorio tiene 8 clusters
    if not os.path.exists(IMG_PATH):
        print(f"[ERROR] No se encontró el archivo en: {IMG_PATH}")
        return

    with open(IMG_PATH, "rb") as f:
        f.seek(START_OFFSET)
        directorio_bytes = f.read(DIR_SIZE)
        
        # Cabecera 
        print(f"\n{'Nombre Archivo':<16} | {'Tamaño':<10} | {'Cluster Inicial':<12} | {'Creación':<20} | {'Modificación':<20}")
        print("-" * 95)
        
        for i in range(0, DIR_SIZE, ENTRY_SIZE):
            entrada = directorio_bytes[i : i + ENTRY_SIZE]
          
            if entrada[0:1] == b'/': #CON ESTE IF YA NO MUESTRA LOS VACIOS-----------------------------------------------------------------------
               continue
            
            # 1-16 nombre archivo
            bytes_nombre = entrada[1:16].split(b'\x00')[0]
            nombre = bytes_nombre.decode('ascii').strip()
                            
            # 16-20 tamaño archivo
            tamano = struct.unpack('<I', entrada[16:20])[0]
            
            # 4. 20-23 cluster inicial
            cluster_inicial = struct.unpack('<I', entrada[20:24])[0]
            
            # 5.30-43 fecha y hora de creacion
            bytes_creacion = entrada[30:44].split(b'\x00')[0]
            fecha_creacion_raw = bytes_creacion.decode('ascii').strip()
            fecha_creacion = formatear_fecha(fecha_creacion_raw)
            
            # 6. 50-63 fecha y hora de ultima modificacion
            bytes_modificacion = entrada[50:64].split(b'\x00')[0]
            fecha_mod_raw = bytes_modificacion.decode('ascii').strip()
            fecha_mod = formatear_fecha(fecha_mod_raw)
            
            # imprimir fila 
            print(f"{nombre:<16} | {tamano:<10} | {cluster_inicial:<15} | {fecha_creacion:<20} | {fecha_mod:<20}")

def formatear_fecha(cadena_fecha):
    """Convierte '20260108182600' en '2026-01-08 18:26:00' para que sea legible."""
    if len(cadena_fecha) < 14:
        return "Fecha inválida"
    anio = cadena_fecha[0:4]
    mes = cadena_fecha[4:6]
    dia = cadena_fecha[6:8]
    hora = cadena_fecha[8:10]
    minuto = cadena_fecha[10:12]
    segundo = cadena_fecha[12:14]
    return f"{anio}-{mes}-{dia} {hora}:{minuto}:{segundo}"



if __name__ == "__main__":
    analizar_superbloque()
    listar_directorio()
