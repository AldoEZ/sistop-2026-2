#include <bits/stdc++.h>
//#include <ctime>
//#include <iomanip>

using namespace std;

struct Proceso{
    char id;
    int t_llegada;
    int t_servicio;
    int t_restante;
    int t_fin;
};

vector<Proceso> generarProcesos(){
    vector<Proceso> lista;
    for(int i = 0; i < 5; ++i){
        Proceso p;
        p.id = 'A' + i;
        p.t_llegada = rand() % 11;    //0 - 10 
        p.t_servicio = (rand() % 8) + 1; //1 - 8 
        p.t_restante = p.t_servicio;
        lista.push_back(p);
    }
    //Ordena de menor a mayor para facilitar el proceso
    sort(lista.begin(), lista.end(), [](const Proceso& a, const Proceso& b){
        return a.t_llegada < b.t_llegada;
    });
    return lista;
}

void calcularPromedio(vector<Proceso> procesos, string nombreAlgoritmo, string diagrama){
    //Función para calcular promedio de tiempo de retorno, espera y penalización
    double sumaT = 0, sumaE = 0, sumaP = 0;
    int n = procesos.size();

    for(const auto& p : procesos){
        int T = p.t_fin - p.t_llegada;
        int E = T - p.t_servicio;
        double P = (double)T / p.t_servicio;

        sumaT += T;
        sumaE += E;
        sumaP += P;
    }

    cout << "  " << nombreAlgoritmo << ": T = " << fixed << setprecision(1) << (sumaT / n) << ", E = " << (sumaE / n) << ", P = " << setprecision(2) << (sumaP / n) << "\n" << "    " << diagrama << "\n";
}

void algoritmoFCFS(vector<Proceso> procesos){
    int tiempoActual = 0;
    string diagrama = "";
    
    for(int i = 0; i < procesos.size(); i++){
        //Si no hay proceso que atender marcamos con - para su representación
        if(tiempoActual < procesos[i].t_llegada){
            int espera = procesos[i].t_llegada - tiempoActual;
            for(int j = 0; j < espera; j++) diagrama += "-"; //Rellenamos el tiempo de espera -
            tiempoActual = procesos[i].t_llegada;
        }

        for(int j = 0; j < procesos[i].t_servicio; j++){
            diagrama += procesos[i].id;
            tiempoActual++;
        }
        procesos[i].t_fin = tiempoActual;
    }

    calcularPromedio(procesos, "FCFS", diagrama);
}

void algoritmoRR(vector<Proceso> procesos, int quantum){
    int tiempoActual = 0;
    string diagrama = "";
    queue<int> colaListos;
    int terminados = 0;
    int n = procesos.size();
    
        
    int i = 0; //Indica el idx  para saber que procesos han llegado
    
    while(terminados < n){
        //Agregamos procesos que llegan a la cola
        while(i < n && procesos[i].t_llegada <= tiempoActual){
            colaListos.push(i);
            i++;
        }
        //Si esta vacio, significa que no esta haciendo nada
        if(colaListos.empty()){
            diagrama += "-"; //- significa que no hay nada que hacer
            tiempoActual++;
            continue;
        }

        //Tomamos el proceso que ya este listo y lo sacamos 
        int idx = colaListos.front();
        colaListos.pop();

        //Decidimos cual es el tiempo necesario que se necesita y si es que el quantum lo ofrece
        int tiempoEjecucion = min(quantum, procesos[idx].t_restante);
        
        for(int j = 0; j < tiempoEjecucion; j++){
            diagrama += procesos[idx].id;
            tiempoActual++;
            
            //Verificamos si hay mas procesos en espera
            while(i < n && procesos[i].t_llegada <= tiempoActual){
                colaListos.push(i);
                i++;
            }
        }
        
        procesos[idx].t_restante -= tiempoEjecucion;

        //Si no t_finaliza el proceso lo volvemos a acomodar en la cola
        if(procesos[idx].t_restante > 0){
            colaListos.push(idx);
        }else{
            procesos[idx].t_fin = tiempoActual;
            terminados++;
        }
    }

    string nombre = "RR" + to_string(quantum);
    calcularPromedio(procesos, nombre, diagrama);
}

void algoritmoSPN(vector<Proceso> procesos){
    int tiempoActual = 0;
    string diagrama = "";
    int terminados = 0;
    int n = procesos.size();
    vector<bool> t_finalizado(n, false);

    while(terminados < n){
        //Para poder compararlo de manera correcta y sacar el minimo
        int indiceMejor = -1;
        int minServicio = 10; 

        //Buscar el proceso más corto de los que ya llegaron y que no hemos t_finalizado
        for(int i = 0; i < n; i++){
            if(procesos[i].t_llegada <= tiempoActual && !t_finalizado[i]){
                if(procesos[i].t_servicio < minServicio){
                    minServicio = procesos[i].t_servicio;
                    indiceMejor = i; //El mejor proceso == minimo tiempo
                }
            }
        }

        //Si un proceso mejor imprimimos - para representar descanso 
        if(indiceMejor == -1){
            diagrama += "-";
            tiempoActual++;
            continue;
        }

        //Ejecutar el proceso hasta el t_final
        for(int j = 0; j < procesos[indiceMejor].t_servicio; j++){
            diagrama += procesos[indiceMejor].id;
            tiempoActual++;
        }
        
        //Actulizamos vector de procesos t_finalizados y el tiempo
        procesos[indiceMejor].t_fin = tiempoActual;
        t_finalizado[indiceMejor] = true;
        terminados++;
    }

    calcularPromedio(procesos, "SPN", diagrama);
}

void algoritmoFB(vector<Proceso> procesos){
    int tiempoActual = 0;
    string diagrama = "";
    queue<int> colas[3];
    int quantums[3] = {1, 2, 4}; //Quantums para cada nivel
    int terminados = 0;
    int n = procesos.size();
    int i = 0;

    //Vector para rastrear en qué nivel está cada proceso, todps inician en 0 | 1= maximo, 2 = minima
    vector<int> nivelActual(n, 0);

    while(terminados < n){
        //Agregamos procesos que llegan en este segundo a la Cola 0
        while(i < n && procesos[i].t_llegada <= tiempoActual){
            colas[0].push(i);
            i++;
        }

        //Buscamos la cola con mayor prioridad
        int nivel = -1;
        for(int j = 0; j < 3; j++){
            if(!colas[j].empty()){
                nivel = j;
                break;
            }
        }

        //Si no hay nadie, marcamos con - esos descansos
        if(nivel == -1){
            diagrama += "-";
            tiempoActual++;
            continue;
        }

        //Atender al proceso que hay en ese nivel
        int idx = colas[nivel].front();
        colas[nivel].pop();

        int q = quantums[nivel];
        int tiempoEjecucion = min(q, procesos[idx].t_restante);

        for(int k = 0; k < tiempoEjecucion; k++){
            diagrama += procesos[idx].id;
            tiempoActual++;
            
            //Revisamos si llegan nuevos procesos 
            while(i < n && procesos[i].t_llegada <= tiempoActual){
                colas[0].push(i);
                i++;
            }
        }

        procesos[idx].t_restante -= tiempoEjecucion;

        //Dependiendo no termino baja de nivel como castigo
        if(procesos[idx].t_restante > 0){
            int nuevoNivel = min(nivel + 1, 2);
            colas[nuevoNivel].push(idx);
        }else{
            procesos[idx].t_fin = tiempoActual;
            terminados++;
        }
    }

    calcularPromedio(procesos, "FB", diagrama);
}

int main(){
    //Pa ra que los números aleatorios cambien en cada ejecución
    srand(time(0));

    cout << "====================================================" << "\n";
    cout << "       SIMULADOR DE PLANIFICACION DE PROCESOS       " << "\n";
    cout << "====================================================" << "\n";

    for(int r = 1; r <= 5; ++r){
        cout << "\n- Ronda " << r << ":" <<  "\n";

        //Generamos los valores aleatorios
        vector<Proceso> carga = generarProcesos();

        //Imprimimos los procesos con sus valores
        int t_servicioTotal = 0;
        cout << "  ";
        for(size_t i = 0; i < carga.size(); ++i){
            cout << carga[i].id << ": " << carga[i].t_llegada << ", t=" << carga[i].t_servicio;
            if(i < carga.size() - 1) cout << "; ";
            t_servicioTotal += carga[i].t_servicio;
        }
        cout << " (tot:" << t_servicioTotal << ")" << "\n";

        //Ejecución de los algoritmos planificadores
        algoritmoFCFS(carga);
        algoritmoRR(carga, 1); //RR quantum 1
        algoritmoRR(carga, 4); //RR quantum 4
        algoritmoSPN(carga);
        algoritmoFB(carga);    

        cout << "----------------------------------------------------" << "\n";
    }

    cout << "\nFin de algoritmos de planificadores" << "\n";
    return 0;
}
