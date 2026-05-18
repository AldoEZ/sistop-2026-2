#include <bits/stdc++.h>
#include <ctime>

using namespace std;

#define pb push_back				
#define sz(a) int(a.size())
const int INF = INT_MAX;

struct Proceso {
    char id;
    int llegada;
    int unidadesCPU;
    int restante;
    int finalizacion;
    int queue_level;
};

struct Resultado {
    double T = 0.0;
    double E = 0.0;
    double P = 0.0;
    string orden_procesos;
};

void mostrar_procesos(const vector<Proceso>& procesos) {
    cout << "  ";
    int n = sz(procesos);
    for(int i = 0; i < n; i++) {
        cout << procesos[i].id << ": " << procesos[i].llegada << ", t = " << procesos[i].unidadesCPU;
        if(i + 1 < n) cout << "; ";
    }
    cout << '\n';
}

void mostrar_resultados(const string& name, const Resultado& r) {
    cout << "  " << name
        << ": T = " << fixed << setprecision(1) << r.T
        << ", E = " << r.E
        << ", P = " << setprecision(2) << r.P << '\n';
    cout << "  " << r.orden_procesos << '\n';
}

vector<Proceso> ejemplo_tarea() {
    vector<Proceso> procesos;
    
    procesos.pb(Proceso{'A', 0, 3, 3, -1, 0});
    procesos.pb(Proceso{'B', 1, 5, 5, -1, 0});
    procesos.pb(Proceso{'C', 3, 2, 2, -1, 0});
    procesos.pb(Proceso{'D', 9, 5, 5, -1, 0});
    procesos.pb(Proceso{'E', 12, 5, 5, -1, 0});
    
    return procesos;
}

vector<Proceso> generar_proceso(int n) {
    vector<Proceso> procesos;
    
    int llegada = 0;
    for(int i = 0; i < n; i++) {
        if(i != 0) llegada += (rand() % 4);
        
        int unidadesCPU = 1 + rand() % 8;
        
        procesos.pb(Proceso{char('A'+i), llegada, unidadesCPU, unidadesCPU, -1, 0});
    }
    
    return procesos;
}

Resultado calculo_resultado(const vector<Proceso>& procesos, const string& orden_procesos) {
    Resultado r;
    r.orden_procesos = orden_procesos;
    
    for(const auto& proceso : procesos) {
        double t = proceso.finalizacion - proceso.llegada;
        double e = t - proceso.unidadesCPU;
        double p = t/double(proceso.unidadesCPU);
        
        r.T += t;
        r.E += e;
        r.P += p;
    }
    
    int n = sz(procesos);
    if(n > 0) {
        r.T /= n;
        r.E /= n;
        r.P /= n;
    }
    
    return r;
}

Resultado fcfs(vector<Proceso> procesos) {
    queue<int> p_listos;
    string orden_procesos;
    int tiempo = 0;
    int siguiente = 0;
    int completado = 0;
    int n = sz(procesos);
    
    while(completado < n) {
        while(siguiente < n && procesos[siguiente].llegada <= tiempo) {
            p_listos.push(siguiente);
            siguiente++;
        }
        
        if(p_listos.empty()) {
            if(siguiente < n) {
                orden_procesos.append(procesos[siguiente].llegada - tiempo, '_');
                tiempo = procesos[siguiente].llegada;
                continue;
            }
            break;
        }
        
        int idx = p_listos.front();
        p_listos.pop();
        
        for(int k = 0; k < procesos[idx].restante; k++) {
            orden_procesos.pb(procesos[idx].id);
            tiempo++;
        }
        
        procesos[idx].restante = 0;
        procesos[idx].finalizacion = tiempo;
        completado++;
    }
    
    return calculo_resultado(procesos, orden_procesos);
}

Resultado rr(vector<Proceso> procesos, int quantum) {
    queue<int> p_listos;
    string orden_procesos;
    int tiempo = 0;
    int siguiente = 0;
    int completado = 0;
    int n = sz(procesos);
    
    while(completado < n) {
        while(siguiente < n && procesos[siguiente].llegada <= tiempo) {
            p_listos.push(siguiente);
            siguiente++;
        }
        
        if(p_listos.empty()) {
            if (siguiente < n) {
                orden_procesos.append(procesos[siguiente].llegada - tiempo, '_');
                tiempo = procesos[siguiente].llegada;
                continue;
            }
            break;
        }
        
        int idx = p_listos.front();
        p_listos.pop();
        
        int slice = min(quantum, procesos[idx].restante);
        for(int used = 0; used < slice; used++) {
            orden_procesos.pb(procesos[idx].id);
            tiempo++;
            procesos[idx].restante--;
            
            while(siguiente < n && procesos[siguiente].llegada <= tiempo) {
                p_listos.push(siguiente);
                siguiente++;
            }
            
            if(procesos[idx].restante == 0) {
                procesos[idx].finalizacion = tiempo;
                completado++;
                break;
            }
        }
        
        if(procesos[idx].restante > 0) p_listos.push(idx);
    }
    
    return calculo_resultado(procesos, orden_procesos);
}

Resultado spn(vector<Proceso> procesos) {
    string orden_procesos;
    int tiempo = 0;
    int completado = 0;
    int n = sz(procesos);
    
    while(completado < n) {
        int op = -1;
        
        for(int i = 0; i < n; i++) {
            if(procesos[i].restante <= 0) continue;
            if(procesos[i].llegada > tiempo) continue;
            
            if(op == -1) {
                op = i;
            } else {
                if(procesos[i].unidadesCPU != procesos[op].unidadesCPU) {
                    if(procesos[i].unidadesCPU < procesos[op].unidadesCPU) op = i;
                } else if(procesos[i].llegada != procesos[op].llegada) {
                    if(procesos[i].llegada < procesos[op].llegada) op = i;
                } else if(procesos[i].id < procesos[op].id) {
                    op = i;
                }
            }
        }
        
        if(op == -1) {
            int sig_proceso = INF;
            for(int i = 0; i < n; i++) {
                if(procesos[i].restante > 0)
                    sig_proceso = min(sig_proceso, procesos[i].llegada);
            }
            
            if(sig_proceso == INF) break;
            
            orden_procesos.append(sig_proceso - tiempo, '_');
            tiempo = sig_proceso;
            continue;
        }
        
        for(int k = 0; k < procesos[op].restante; k++) {
            orden_procesos.pb(procesos[op].id);
            tiempo++;
        }
        
        procesos[op].restante = 0;
        procesos[op].finalizacion = tiempo;
        completado++;
    }
    
    return calculo_resultado(procesos, orden_procesos);
}

Resultado fb(vector<Proceso> procesos) {
    const int NIVELES = 4;
    array<int, NIVELES> quantums = {1, 2, 4, 8};
    vector<deque<int>> mult_colas(NIVELES);
    
    string orden_procesos;
    int tiempo = 0;
    int siguiente = 0;
    int completado = 0;
    int n = sz(procesos);
    
    int actual = -1;
    int nivel_actual = -1;
    int usado = 0;
    
    auto llegadas = [&]() {
        while(siguiente < n && procesos[siguiente].llegada <= tiempo) {
            procesos[siguiente].queue_level = 0;
            mult_colas[0].pb(siguiente);
            siguiente++;
        }
    };
    
    while(completado < n) {
        llegadas();
        
        if(actual != -1) {
            bool p_listo = false;
            for(int l = 0; l < nivel_actual; l++) {
                if (!mult_colas[l].empty()) {
                    p_listo = true;
                    break;
                }
            }
            
            if(p_listo) {
                mult_colas[nivel_actual].pb(actual);
                actual = -1;
                nivel_actual = -1;
                usado = 0;
            }
        }
        
        if(actual == -1) {
            for(int l = 0; l < NIVELES; l++) {
                if(!mult_colas[l].empty()) {
                    actual = mult_colas[l].front();
                    mult_colas[l].pop_front();
                    nivel_actual = l;
                    usado = 0;
                    break;
                }
            }
        }
        
        if(actual == -1) {
            if(siguiente < n) {
                orden_procesos.append(procesos[siguiente].llegada - tiempo, '_');
                tiempo = procesos[siguiente].llegada;
                continue;
            }
            break;
        }
        
        orden_procesos.pb(procesos[actual].id);
        tiempo++;
        procesos[actual].restante--;
        usado++;
        
        llegadas();
        
        if(procesos[actual].restante == 0) {
            procesos[actual].finalizacion = tiempo;
            completado++;
            actual = -1;
            nivel_actual = -1;
            usado = 0;
            continue;
        }
        
        if(usado == quantums[nivel_actual]) {
            int otro_nivel = min(nivel_actual + 1, NIVELES - 1);
            procesos[actual].queue_level = otro_nivel;
            mult_colas[otro_nivel].pb(actual);
            actual = -1;
            nivel_actual = -1;
            usado = 0;
        }
    }
    
    return calculo_resultado(procesos, orden_procesos);
}

void ej_ronda(vector<Proceso>& procesos, string& ronda) {
    cout << ronda << '\n';
    mostrar_procesos(procesos);
    
    Resultado r_fcfs = fcfs(procesos);
    Resultado r_rr1 = rr(procesos, 1);
    Resultado r_rr4 = rr(procesos, 4);
    Resultado r_spn = spn(procesos);
    Resultado r_fb = fb(procesos);
    
    mostrar_resultados("FCFS", r_fcfs);
    mostrar_resultados("RR1 ", r_rr1);
    mostrar_resultados("RR4 ", r_rr4);
    mostrar_resultados("SPN ", r_spn);
    mostrar_resultados("FB  ", r_fb);
}

int main() {
    srand(time(0));
    
    vector<Proceso> ejemplo = ejemplo_tarea();
    string a = "- Caso de ejemplo de la tarea:";
    
    ej_ronda(ejemplo, a);
    cout << '\n';
	
    int rondas = 5, num_procesos = 5;
    for(int ronda = 1; ronda <= rondas; ronda++) {
        vector<Proceso> procesos = generar_proceso(num_procesos);
        string nombre = "- Ronda " + to_string(ronda);
        ej_ronda(procesos, nombre);
        if(ronda != rondas) cout << '\n';
    }
    
    return 0;
}
