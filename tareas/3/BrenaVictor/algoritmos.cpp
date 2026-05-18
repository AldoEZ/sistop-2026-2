//#include <bits/stdc++.h>
#include <iostream>
#include <vector>
#include <algorithm>
#include <queue>
#include <iomanip>
#include <string>
#include <ctime>
#include <cstdlib>

using namespace std;

struct Proceso{
    char id;
    int llegada;
    int requerido;    
    int restante;  
    int fin;
    int T, E;     
    double P;     
};

// Calcula metricas de cada proceso
void metricas(Proceso &p){
    p.T= p.fin-p.llegada;
    p.E= p.T-p.requerido;
    p.P=(double)p.T / p.requerido;
}

// Imprime los promedios y el esquema
void imprimirResultados(vector<Proceso> v, string nombre, string esquema){
    double sumT=0, sumE=0, sumP=0;
    cout <<endl <<nombre <<endl;
    for(auto &p:v){
        metricas(p);
        sumT += p.T; sumE += p.E; sumP += p.P;
    }
    int n= v.size();
    cout <<"Promedio: \t T=" <<sumT/n <<"\tE=" <<sumE/n <<"\tP=" <<sumP/n <<endl;
    cout<<"Esquema: "<<esquema <<endl;
}

// Generador de pruebas aleatorias
vector<Proceso> generarPrueba(){
    vector<Proceso> procesos;
    vector<char> proc={'A', 'B', 'C', 'D', 'E'};
    for(int i=0; i<5; i++){
        int llegada= rand() % 15;
        int t= 1+rand() % 8;
        procesos.push_back({proc[i], llegada, t, t, 0, 0, 0, 0});
    }
    // Ordenar por llegada inicial es vital para todos los algoritmos
    sort(procesos.begin(), procesos.end(), [](Proceso a, Proceso b){
    if(a.llegada == b.llegada) return a.id < b.id;
        return a.llegada < b.llegada;
    });
    return procesos;
}

// Algoritmo First Come, First Serve
void FCFS(vector<Proceso> procesos){
    int tiempoActual= 0;
    string esquema= "";

    for(int i= 0; i<procesos.size(); i++){
        // Espera a el ingreso de un proceso
        if(tiempoActual<procesos[i].llegada){
            tiempoActual= procesos[i].llegada;
        }

        // Se ejecuta todo el proceso completo
        for(int j= 0; j<procesos[i].requerido; j++){
            esquema += procesos[i].id;
        }

        tiempoActual += procesos[i].requerido;
        procesos[i].fin= tiempoActual;
    }

    imprimirResultados(procesos, "FCFS", esquema);
}

// Algoritmo generalizado de Round Robin
// Se ingresa el quantum deseado
void RoundRobin(vector<Proceso> procesos, int q){
    int n= procesos.size();
    int tiempoActual= 0;
    int terminados= 0;
    string esquema= "";
    queue<int> colaIndices;
    vector<bool> enCola(n, false);

    while(terminados<n){
        //Meter a la cola los procesos que acaban de llegar en este segundo
        for(int i= 0; i<n; i++){
            if(!enCola[i] && procesos[i].llegada <= tiempoActual){
                colaIndices.push(i);
                enCola[i]= true;
            }
        }
        //Si no hay nadie listo, avanzamos y volvemos a intentar
        if(colaIndices.empty()){
            tiempoActual++;
            continue;
        }
        //Tomar el siguiente proceso de la cola
        int idx= colaIndices.front();
        colaIndices.pop();

        //Ejecutar por el quantum o lo que reste
        int tiempoEjecucion= min(procesos[idx].restante, q);
        
        for(int i= 0; i<tiempoEjecucion; i++){
            esquema += procesos[idx].id;
            tiempoActual++;
            //Revisa si llegaron procesos mientras este se ejecutaba
            for(int j= 0; j<n; j++){
                if(!enCola[j] && procesos[j].llegada <= tiempoActual){
                    colaIndices.push(j);
                    enCola[j]= true;
                }
            }
        }

        procesos[idx].restante -= tiempoEjecucion;

        // E. Si no ha terminado, regresa al final de la cola
        if(procesos[idx].restante > 0){
            colaIndices.push(idx);
        } else{
            procesos[idx].fin= tiempoActual;
            terminados++;
        }
    }

    imprimirResultados(procesos, "RR"+to_string(q), esquema);
}

// Algoritmo Shortest Process Next
void SPN(vector<Proceso> v){
    int n= v.size();
    int tiempoActual= 0;
    string esquema= "";
    vector<bool> listo(n, false); // Para marcar quien ya termino

    for(int i= 0; i<n; i++){
        int aux= -1;

        // Buscar el proceso con requerido minima que ya haya llegado
        for(int j= 0; j<n; j++){
            if(!listo[j] && v[j].llegada <= tiempoActual){
                if(aux== -1 || v[j].requerido<v[aux].requerido){
                    aux= j;
                }
            }
        }

        // Si no encontré a nadie que haya llegado, salto el tiempo al siguiente proceso
        if(aux== -1){
            int proximaLlegada= 1e9;
            for(int j=0; j<n; j++) 
                if(!listo[j]) proximaLlegada= min(proximaLlegada, v[j].llegada);
            
            tiempoActual= proximaLlegada;
            i--; 
            continue;
        }

        // Se ejecuta todo el proceso completo
        for(int j= 0; j<v[aux].requerido; j++) esquema += v[aux].id;
        
        v[aux].fin= tiempoActual+v[aux].requerido;
        tiempoActual= v[aux].fin;
        listo[aux]= true;
    }
    imprimirResultados(v, "SPN", esquema);
}

int main(){
    srand(time(NULL));
    vector<vector<Proceso>> pruebas;
    int num_pruebas=3;
    //Pruebas ejemplo dadas por el profesor
    vector<Proceso> prueba1={
       {'A',0,3,3},
       {'B',1,5,5},
       {'C',3,2,2},
       {'D',9,5,5},
       {'E',12,5,5}
    };

    vector<Proceso> prueba2={
       {'A',0,5,5},
       {'B',3,3,3},
       {'C',3,7,7},
       {'D',7,4,4},
       {'E',8,4,4}
    };
    
    // Ingreso de las pruebas de ejemplo
    pruebas.push_back(prueba1);
    pruebas.push_back(prueba2);

    //Generacion de 3 pruebas nuevas al azar
    for(int i=0; i<num_pruebas;i++){
        vector<Proceso> prueba=generarPrueba();
        pruebas.push_back(prueba);
    }
    vector<string> ronda={"Primera", "Segunda", "Tercera", "Cuarta", "Quinta"};

    //Se procesan las 5 pruebas
    for(int i=0; i<5;i++){

        cout<<endl<<"------ "<<ronda[i]<<" ronda:"<<endl;

        // Detalles de cada una de las pruebas
        int tot=0;
        for(auto &p:pruebas[i]){
            cout<<p.id<<": "<<p.llegada<<", t="<<p.requerido<<"; ";
            tot+=p.requerido;
        }
        cout<<endl<<"(tot:"<<tot<<")"<<endl;
        //Ejecucion de los algoritmos
        FCFS(pruebas[i]);
        RoundRobin(pruebas[i],1);
        RoundRobin(pruebas[i],4);
        SPN(pruebas[i]);
    }
    return 0;
}