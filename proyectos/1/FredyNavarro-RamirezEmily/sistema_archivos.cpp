#include "sistema_archivos.h"
#include "estructuras.h"
#include <iostream>
#include <fstream>
#include <string>
#include <vector>

using namespace std;

bool validar_superbloque(){
    ifstream disco(RUTA_DISCO, ios::binary);
    if(!disco.is_open()){
        cerr << "[Error] No se pudo abrir " << RUTA_DISCO << "\n";
        return false;
    }

    Superbloque sb;
    disco.read(reinterpret_cast<char*>(&sb), sizeof(Superbloque));
    disco.close();

    string nombre(sb.nombre_fs, 9);
    string version(sb.version, 5);
    nombre.erase(nombre.find_last_not_of('\x00') + 1);
    version.erase(version.find_last_not_of('\x00') + 1);

    if(nombre != "FiUnamFS" || version != "26-2"){
        cerr << "[Fatal] Archivo corrupto o versión incorrecta.\n";
        return false;
    }

    cout << "[FS] Disco validado. Cluster: " << sb.tamano_cluster << " bytes.\n";
    return true;
}

void listar_directorio(){
    ifstream disco(RUTA_DISCO, ios::binary);
    if(!disco.is_open()){
        cerr << "[Error] No se pudo abrir " << RUTA_DISCO << "\n";
        return;
    }

    cout << "\n--- Contenido de FiUnamFS ---\n";
    cout << "Nombre\t\tTamaño(B)\tCluster\tFecha Creación\n";
    cout << "--------------------------------------------------------------\n";

    disco.seekg(1 * TAMANO_CLUSTER); //Saltamos al cluster 1

    for(int i = 0; i < ENTRADAS_POR_DIRECTORIO; ++i){
        EntradaDirectorio entrada;
        disco.read(reinterpret_cast<char*>(&entrada), sizeof(EntradaDirectorio));

        if(entrada.tipo == '-'){
            string nombre(entrada.nombre, 15);
            string fecha(entrada.fecha_creacion, 14);
            
            //Eliminamos espacios y nulos al final para evitar problemas de formato
            size_t fin_nombre = nombre.find_last_not_of(" \x00");
            if(fin_nombre != string::npos){
                nombre.erase(fin_nombre + 1);
            }else{
                nombre.clear();
            }

            if(nombre != "###############" && !nombre.empty()){
                cout << nombre << "\t" 
                          << entrada.tamano << "\t\t" 
                          << entrada.cluster_inicial << "\t"
                          << fecha << "\n";
            }
        }
    }
    
    disco.close();
    cout << "--------------------------------------------------------------\n";
}

void copiar_desde_fs(const string& archivo_origen, const string& archivo_destino){
    ifstream disco(RUTA_DISCO, ios::binary);
    if(!disco.is_open()) return;

    disco.seekg(1 * TAMANO_CLUSTER);
    bool encontrado = false;
    EntradaDirectorio archivo_info;

    for(int i = 0; i < ENTRADAS_POR_DIRECTORIO; ++i){
        disco.read(reinterpret_cast<char*>(&archivo_info), sizeof(EntradaDirectorio));

        if(archivo_info.tipo == '-'){
            string nombre(archivo_info.nombre, 15);
            size_t fin_nombre = nombre.find_last_not_of(" \x00");
            if(fin_nombre != string::npos) nombre.erase(fin_nombre + 1);
            else nombre.clear();

            if(nombre == archivo_origen){
                encontrado = true;
                break;
            }
        }
    }

    if(!encontrado){
        cout << "[Error] El archivo '" << archivo_origen << "' no existe en FiUnamFS.\n";
        disco.close();
        return;
    }

    cout << "[FS] Extrayendo '" << archivo_origen << "' (" << archivo_info.tamano << " bytes)\n";

    //Saltamos al cluster de datos
    disco.seekg(archivo_info.cluster_inicial * TAMANO_CLUSTER);
    vector<char> buffer(archivo_info.tamano);
    disco.read(buffer.data(), archivo_info.tamano);
    disco.close();

    //Escribimos en la PC local
    ofstream salida(archivo_destino, ios::binary);
    if(!salida.is_open()){
        cerr << "[Error] No se pudo crear el archivo local '" << archivo_destino << "'\n";
        return;
    }

    salida.write(buffer.data(), archivo_info.tamano);
    salida.close();
    cout << "[FS] Archivo guardado exitosamente como '" << archivo_destino << "'\n";
}

void eliminar_archivo(const string& archivo_borrar){
    //Abrimos con fstream para leer y escribir al mismo tiempo
    fstream disco(RUTA_DISCO, ios::in | ios::out | ios::binary);
    if(!disco.is_open()){
        cerr << "[Error] No se pudo abrir " << RUTA_DISCO << "\n";
        return;
    }

    disco.seekg(1 * TAMANO_CLUSTER);
    bool encontrado = false;
    EntradaDirectorio entrada;

    for(int i = 0; i < ENTRADAS_POR_DIRECTORIO; ++i){
        long posicion_actual = disco.tellg();
        disco.read(reinterpret_cast<char*>(&entrada), sizeof(EntradaDirectorio));

        if(entrada.tipo == '-'){
            string nombre(entrada.nombre, 15);
            size_t fin_nombre = nombre.find_last_not_of(" \x00");
            if(fin_nombre != string::npos) nombre.erase(fin_nombre + 1);
            else nombre.clear();

            if(nombre == archivo_borrar){
                encontrado = true;

                //Retrocedemos el cabezal para sobrescribir
                disco.seekp(posicion_actual);

                char tipo_borrado = '/';
                string nombre_borrado = "###############";

                disco.write(&tipo_borrado, 1);
                disco.write(nombre_borrado.c_str(), 15);

                cout << "[FS] Archivo '" << archivo_borrar << "' eliminado lógicamente.\n";
                break;
            }
        }
    }

    if(!encontrado){
        cout << "[Error] El archivo '" << archivo_borrar << "' no existe en FiUnamFS.\n";
    }

    disco.close();
}
