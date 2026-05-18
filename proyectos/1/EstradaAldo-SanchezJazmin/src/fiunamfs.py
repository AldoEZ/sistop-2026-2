"""
logica utilizada para interpretar la imagen FiUnamFS
"""

from disco import Disco
from constantes import (
    NOMBRE_SISTEMA, VERSION, TAM_CLUSTER,
    CLUSTER_INICIO_DIRECTORIO,
    CLUSTER_FINAL_DIRECTORIO,
    TAM_ENTRADA_DIRECTORIO
)
from entrada_directorio import EntradaDirectorio

"""
clase que representa el sistema de archivos contenido en la imagen
"""
class FiUnamFS:
    def __init__(self, ruta_imagen):
        self.ruta_imagen = ruta_imagen
        self.disco = Disco(ruta_imagen)
    
    """
    funcion que lee una cadena ASCII de la imagen usando un rango [inicio,fin)
    """
    def leer_cadena(self, inicio, fin):
        datos = self.disco.leer_bytes(inicio, fin - inicio)
        
        return datos.decode("ascii").strip("\x00").strip()
    
    """
    valida que la imagen sea la correspondiente a FiUnamFS con la version 2026-2
    """
    def validar_superbloque(self):
        nombre_sistema = self.leer_cadena(5,13)
        version = self.leer_cadena(14,18)
        
        if nombre_sistema != NOMBRE_SISTEMA:
            print(f"Error: sistema de archivos incorrecto: '{nombre_sistema}'")
            return False
        
        if version != VERSION:
            print(f"Error: version de sistema de archivos incorrecta: '{version}'")
            return False
        
        return True
    
    """
    lectura de todas las entradas del directorio FiUnamFS
    """
    def leer_directorio(self):
        entradas = []
        
        offset_directorio = CLUSTER_INICIO_DIRECTORIO * TAM_CLUSTER
        tamano_directorio = (CLUSTER_FINAL_DIRECTORIO - CLUSTER_INICIO_DIRECTORIO + 1) * TAM_CLUSTER
        
        datos_directorio = self.disco.leer_bytes(offset_directorio, tamano_directorio)
        
        total_entradas = tamano_directorio // TAM_ENTRADA_DIRECTORIO
        
        for indice in range(total_entradas):
            inicio = indice * TAM_ENTRADA_DIRECTORIO
            fin = inicio + TAM_ENTRADA_DIRECTORIO
            
            datos_entrada = datos_directorio[inicio:fin]
            entrada = EntradaDirectorio.crear_entrada_directorio(datos_entrada, indice)
            
            entradas.append(entrada)
        
        return entradas
    
    """
    se regresa una lisata con los archivos existentes en FiUnamFS
    """
    def listar_archivos(self):
        entradas = self.leer_directorio()
        archivos = []
        
        for entrada in entradas:
            if entrada.es_archivo():
                archivos.append(entrada)
        
        return archivos
