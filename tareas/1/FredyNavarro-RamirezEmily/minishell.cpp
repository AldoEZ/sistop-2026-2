//Autores: Navarro Carbajal Fredy Emiliano y Ramírez Terán Emily
#include <iostream>
#include <string>
#include <vector>
#include <sstream>
#include <unistd.h> //Unix standard
#include <sys/wait.h> //Procesos de espera entre padre e hijo
#include <signal.h> //Manejo de interrupciones 
#include <cstring> //Manipulación de memoria
#include <cerrno> //Manejo de código de errores del sistema 

using namespace std;

// Manejador para la recolección de procesos hijos 
void manejador_sigchld(int num_senal){
    //Guardamos errno para evitar la interferencia de las operaciones del bucle principal
    int error_guardado = errno; 

    //Usando la función  waitpid con WNOHANG almacena a los hijos que ya finalizarón
    while(waitpid(-1, NULL, WNOHANG) > 0){}
    errno = error_guardado;
}

int main(){
    //Configuración del manejador de la señal SIGCHLD con sigaction
    struct sigaction accion_senal;
    accion_senal.sa_handler = manejador_sigchld;
    sigemptyset(&accion_senal.sa_mask);
    accion_senal.sa_flags = SA_RESTART | SA_NOCLDSTOP; 
    
    if(sigaction(SIGCHLD, &accion_senal, NULL) == -1){
        perror("Error de la configuracion SIGCHLD");
        return 1;
    }

    //Ignoramos SIGINT (Ctrl+C) 
    signal(SIGINT, SIG_IGN);

    //Variable para recolección de comandos
    string linea_comando;

    //Bucle principal de la minishell
    while(true){
        //Prompt
        cout << "minishell> ";
        
        //Lee la entrada del usuario
        if(!getline(cin, linea_comando)){
            cout << "\n";
            break; 
        }

        //Ignorar si el usuario solo presiono ENTER
        if(linea_comando.empty()) continue;

        //Se analiza la parte sintáctica del comando ingresado
        stringstream flujo_texto(linea_comando);
        string palabra;
        vector<string> argumentos;
        
        //Almacena los argumentos del comando
        while(flujo_texto >> palabra){
            argumentos.push_back(palabra);
        }

        //No existe argumentos 
        if(argumentos.empty()) continue;

        
        //Comando para salir del programa 
        if(argumentos[0] == "exit"){
            break;
        }

        //Si existe otro argumentos preparamos los argumentos en el formato requerido 
        vector<char*> argumentos_c;
        for(size_t i = 0; i < argumentos.size(); ++i){
            argumentos_c.push_back(const_cast<char*>(argumentos[i].c_str()));
        }
        argumentos_c.push_back(nullptr); //Como regla el último argumento de maneja como nulo

        //Creación de un nuevo proceso 
        pid_t id_proceso = fork();

        if(id_proceso < 0){
            perror("Error al crear nuevo proceso con fork()");
        }else if(id_proceso == 0){
            //Proceso hijo
            
            //Restauramos el comportamiento normal de Ctrl+C para el programa hijo, se hace porque sino hereda lo del padre
            signal(SIGINT, SIG_DFL);

            //Reemplaza la memoria del proceso con el programa solicitado
            execvp(argumentos_c[0], argumentos_c.data());
            
            //Si la función execvp retorna el comando fallo
            cerr << "minishell: comando no encontrado: " << argumentos_c[0] << "\n";
            //Terminar el proceso hijo con código de error
            exit(1);
        } 
    }

    return 0;
}
