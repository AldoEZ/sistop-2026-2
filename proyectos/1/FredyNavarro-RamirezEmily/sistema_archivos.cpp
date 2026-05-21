#include "sistema_archivos.h"
#include "estructuras.h"
#include <iostream>
#include <fstream>
#include <string>
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
