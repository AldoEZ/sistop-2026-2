"""
logica utilizada para interpretar la imagen FiUnamFS
"""

from disco import Disco
from constantes import NOMBRE_SISTEMA, VERSION

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
