#!/usr/bin/python3

#Programa encargado de leer entradas del directorio
#Autores: Isaac Campos, Alejandro Martinez
#Fecha de realización: 17 Mayo 2026

import herramientas as h

#Constantes para identificar el tipo de directorio conforme al planteamiento

ARCHIVO_VAL = '-'
ARCHIVO_VACIO = '/'
NOMBRE_VACIO = '###############'

#Se define la clase para los archivos

#Cabe aclarar que se utilizan archivo y entrada para referirse a lo mismo
#Un archivo = entrada(de un directorio)

class EntradaDir:

    def __init__(self, bytes_raw):

        if bytes_raw is None:
            #caso en el que esta vacio
            self.tipo_archivo = ARCHIVO_VACIO
            self.nombre_archivo = NOMBRE_VACIO
            self.tam_archivo = 0
            self.cluster_incial = 0
            self.hf_creado = '00000000000000'
            self.hf_modificado = '00000000000000'
        else:
            self.parsear(bytes_raw)

    #Parseador, se encarga de leer cada segmento del archivo de acuerdo a los requerimientos
    
    def parsear(self,bytes_raw):

        self.tipo_archivo = chr(bytes_raw[0])
        self.nombre_archivo = bytes_raw[1:15].decode('ascii').strip('\x00').strip()
        self.tam_archivo = h.leerLe(bytes_raw[16:20])
        self.cluster_incial = h.leerLe(bytes_raw[20:24])
        self.hf_creado = bytes_raw[30:44].decode('ascii').strip('\x00').strip()
        self.hf_modificado = bytes_raw[50:64].decode('ascii').strip('\x00').strip()

    #Funcion para crear un nuevo archivo, toma el nombre, tamaño y el cluster de inicio de este nuevo archivo
    
    def crearNuevo(self, nombre, tam, inicio):

        self.tipo_archivo = ARCHIVO_VAL
        self.nombre_archivo = nombre[:15].ljust(15, '\x00')
        self.tam_archivo  = tam
        self.cluster_incial = inicio
        self.hf_creado = h.obtenerFechaHora()
        self.hf_modificado = h.obtenerFechaHora()
    
    #Funcion para "eliminar" archivos, en realidad solo se definen como vacíos
    
    def eliminar(self):
        self.tipo_archivo = ARCHIVO_VACIO
        self.nombre_archivo = NOMBRE_VACIO
        self.tam_archivo = 0
        self.cluster_incial = 0
        self.hf_creado = '00000000000000'
        self.hf_modificado = '00000000000000'

    #Funcion para pasar la información de la instancia de vuelta a bytes, util para escribir a disco

    def pasarBytes(self):
        datos = b''
        datos += self.tipo_archivo.encode('ascii')  
        datos += self.nombre_archivo.encode('ascii')[0:15].ljust(15, b'\x00')
        datos += h.escribirLe(self.tam_archivo)
        datos += h.escribirLe(self.cluster_incial)
        datos += b'\x00' * 6
        datos += self.hf_creado.encode('ascii')[0:14].ljust(14, b'\x00')
        datos += b'\x00' * 6
        datos += self.hf_modificado.encode('ascii')[0:14].ljust(14, b'\x00')

        return bytes(datos)

    def __str__(self):
        return (f"Nombre: {self.nombre_archivo.strip()} | "
                f"Tamaño: {self.tam_archivo} bytes | "
                f"Cluster: {self.cluster_incial} | "
                f"Creado: {self.hf_creado}")


#Pruebas para verificar que funciona adecuadamente - Se hizo uso de Claude -> Sonnet 4.6 adaptativo para agilizar la generación de estas pruebas

if __name__ == '__main__':
    # Prueba 1: leer una entrada real del disco
    with open('../fiunamfs.img', 'rb') as f:
        f.seek(1024)
        for i in range(64):             # hay hasta 64 entradas en el directorio
            raw = f.read(64)
            entrada = EntradaDir(raw)
            if entrada.tipo_archivo == ARCHIVO_VAL:   # '-' = entrada válida
                print(f"Entrada {i} tiene archivo: {entrada.nombre_archivo}")
                break

    entrada = EntradaDir(raw)
    print("=== Entrada leída del disco ===")
    print(f"Tipo:     {entrada.tipo_archivo}")
    print(f"Nombre:   {entrada.nombre_archivo}")
    print(f"Tamaño:   {entrada.tam_archivo}")
    print(f"Cluster:  {entrada.cluster_incial}")
    print(f"Creado:   {entrada.hf_creado}")
    print(f"Modificado: {entrada.hf_modificado}")

    # Prueba 2: verificar que pasarBytes devuelve exactamente 64 bytes
    resultado = entrada.pasarBytes()
    print(f"\n=== pasarBytes ===")
    print(f"Longitud: {len(resultado)} bytes (debe ser 64)")

    # Prueba 3: crear una entrada nueva
    nueva = EntradaDir(None)
    nueva.crearNuevo("prueba.txt", 1234, 5)
    print(f"\n=== Entrada nueva ===")
    print(f"Tipo:     {nueva.tipo_archivo}")
    print(f"Nombre:   {nueva.nombre_archivo}")
    print(f"Tamaño:   {nueva.tam_archivo}")
    print(f"Cluster:  {nueva.cluster_incial}")
    print(f"Creado:   {nueva.hf_creado}")
    print(f"Longitud en bytes: {len(nueva.pasarBytes())} (debe ser 64)")

    # Prueba 4: eliminar la entrada y verificar que queda vacía
    nueva.eliminar()
    print(f"\n=== Después de eliminar ===")
    print(f"Tipo:   {nueva.tipo_archivo} (debe ser '/')")
    print(f"Nombre: {nueva.nombre_archivo} (debe ser '###############')")

