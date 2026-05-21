#include <iostream>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <queue>
#include <string>
#include <sstream>
#include <vector>
#include "sistema_archivos.h"
using namespace std;

struct Tarea{
    string operacion;
    string arg1; 
    string arg2; 
};

queue<Tarea> cola_tareas;
mutex mtx_cola;
condition_variable cv;
bool apagar_sistema = false;

void motor_archivos(){
    if(!validar_superbloque()){
        cout << "Apagando motor por seguridad...\n";
        return;
    }

    while(true){
        unique_lock<mutex> lock(mtx_cola);
        cv.wait(lock, []{ return !cola_tareas.empty() || apagar_sistema; });

        if(apagar_sistema && cola_tareas.empty()) break; 

        Tarea tarea = cola_tareas.front();
        cola_tareas.pop();
        lock.unlock(); 

        //Enrutador de comandos
        if(tarea.operacion == "ls"){
            listar_directorio();
        }else if(tarea.operacion == "cp_in" || tarea.operacion == "cp_out" || tarea.operacion == "rm"){
            cout << "\n[Motor] Ejecutando: " << tarea.operacion << " (En construccion)\n";
        }

        cout << "FiUnamFS> ";
        cout.flush();
    }
}

int main() {
    thread hilo_fs(motor_archivos);
    cout << "Iniciando FiUnamFS...\n";
    this_thread::sleep_for(chrono::milliseconds(100));

    while(true){
        cout << "FiUnamFS> ";
        string linea;
        if(!getline(cin, linea)) break; 

        if(linea.empty()) continue;

        istringstream stream(linea);
        string comando;
        stream >> comando;

        //Capturamos los argumentos (nombres de archivos) si los hay
        vector<string> args;
        string arg;
        while(stream >> arg){
            args.push_back(arg);
        }

        if(comando == "exit"){
            lock_guard<mutex> lock(mtx_cola);
            apagar_sistema = true;
            cv.notify_one();
            break;
        } 
        
        Tarea nueva_tarea;
        nueva_tarea.operacion = comando;
        if(args.size() > 0) nueva_tarea.arg1 = args[0];
        if(args.size() > 1) nueva_tarea.arg2 = args[1];
        
        {
            lock_guard<mutex> lock(mtx_cola);
            cola_tareas.push(nueva_tarea);
        }
        cv.notify_one(); 
        this_thread::sleep_for(chrono::milliseconds(50));
    }

    hilo_fs.join();
    return 0;
}
