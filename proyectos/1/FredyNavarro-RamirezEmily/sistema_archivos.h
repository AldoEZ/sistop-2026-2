#ifndef SISTEMA_ARCHIVOS_H
#define SISTEMA_ARCHIVOS_H

#include <string>

const std::string RUTA_DISCO = "fiunamfs.img";
const int TAMANO_CLUSTER = 2048; //4 sectores de 512 bytes
const int ENTRADAS_POR_DIRECTORIO = (8 * TAMANO_CLUSTER) / 64; //256 entradas máximas

bool validar_superbloque();
void listar_directorio(); 
void copiar_desde_fs(const std::string& archivo_origen, const std::string& archivo_destino);
void eliminar_archivo(const std::string& archivo_borrar);

#endif
