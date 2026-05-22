#include <bits/stdc++.h>
using namespace std;

struct Proceso {
    char nombre;
    int llegada;
    int duracion;
    int restante;
    int finalizacion;
};

// ---------------- UTILIDADES ----------------

void imprimir_resultados(string nombre, vector<Proceso> p, string timeline) {
    double T=0, E=0, P=0;

    for (auto &proc : p) {
        int t = proc.finalizacion - proc.llegada;
        int e = t - proc.duracion;
        double p_i = (double)t / proc.duracion;

        T += t;
        E += e;
        P += p_i;
    }

    int n = p.size();
    cout << "  " << nombre << ": T=" << T/n
         << ", E=" << E/n
         << ", P=" << P/n << "\n";

    cout << "  " << timeline << "\n";
}

// ---------------- FCFS ----------------

void FCFS(vector<Proceso> procesos) {
    sort(procesos.begin(), procesos.end(),
         [](auto &a, auto &b){ return a.llegada < b.llegada; });

    int tiempo = 0;
    string timeline;

    for (auto &p : procesos) {
        while (tiempo < p.llegada) {
            timeline += "-";
            tiempo++;
        }

        for (int i = 0; i < p.duracion; i++) {
            timeline += p.nombre;
            tiempo++;
        }

        p.finalizacion = tiempo;
    }

    imprimir_resultados("FCFS", procesos, timeline);
}

// ---------------- ROUND ROBIN ----------------

void RR(vector<Proceso> procesos, int q, string nombre) {
    queue<int> cola;
    int n = procesos.size();
    vector<bool> en_cola(n, false);

    int tiempo = 0, completados = 0;
    string timeline;

    while (completados < n) {

        for (int i = 0; i < n; i++) {
            if (!en_cola[i] && procesos[i].llegada <= tiempo) {
                cola.push(i);
                en_cola[i] = true;
            }
        }

        if (cola.empty()) {
            timeline += "-";
            tiempo++;
            continue;
        }

        int i = cola.front(); cola.pop();

        int uso = min(q, procesos[i].restante);

        for (int t = 0; t < uso; t++) {
            timeline += procesos[i].nombre;
            tiempo++;

            for (int j = 0; j < n; j++) {
                if (!en_cola[j] && procesos[j].llegada <= tiempo) {
                    cola.push(j);
                    en_cola[j] = true;
                }
            }
        }

        procesos[i].restante -= uso;

        if (procesos[i].restante == 0) {
            procesos[i].finalizacion = tiempo;
            completados++;
        } else {
            cola.push(i);
        }
    }

    imprimir_resultados(nombre, procesos, timeline);
}

// ---------------- SPN ----------------

void SPN(vector<Proceso> procesos) {
    int n = procesos.size();
    vector<bool> terminado(n, false);
    int tiempo = 0, completados = 0;
    string timeline;

    while (completados < n) {

        int idx = -1;
        int min_t = INT_MAX;

        for (int i = 0; i < n; i++) {
            if (!terminado[i] && procesos[i].llegada <= tiempo &&
                procesos[i].duracion < min_t) {
                min_t = procesos[i].duracion;
                idx = i;
            }
        }

        if (idx == -1) {
            timeline += "-";
            tiempo++;
            continue;
        }

        for (int i = 0; i < procesos[idx].duracion; i++) {
            timeline += procesos[idx].nombre;
            tiempo++;
        }

        procesos[idx].finalizacion = tiempo;
        terminado[idx] = true;
        completados++;
    }

    imprimir_resultados("SPN", procesos, timeline);
}

// ---------------- FEEDBACK (FB) ----------------

void FB(vector<Proceso> procesos) {
    int n = procesos.size();
    vector<queue<int>> colas(3);

    vector<bool> en_cola(n, false);

    int tiempo = 0, completados = 0;
    string timeline;

    while (completados < n) {

        for (int i = 0; i < n; i++) {
            if (!en_cola[i] && procesos[i].llegada <= tiempo) {
                colas[0].push(i);
                en_cola[i] = true;
            }
        }

        int nivel = -1;
        for (int i = 0; i < 3; i++) {
            if (!colas[i].empty()) {
                nivel = i;
                break;
            }
        }

        if (nivel == -1) {
            timeline += "-";
            tiempo++;
            continue;
        }

        int i = colas[nivel].front();
        colas[nivel].pop();

        int q = pow(2, nivel); // 1,2,4

        int uso = min(q, procesos[i].restante);

        for (int t = 0; t < uso; t++) {
            timeline += procesos[i].nombre;
            tiempo++;

            for (int j = 0; j < n; j++) {
                if (!en_cola[j] && procesos[j].llegada <= tiempo) {
                    colas[0].push(j);
                    en_cola[j] = true;
                }
            }
        }

        procesos[i].restante -= uso;

        if (procesos[i].restante == 0) {
            procesos[i].finalizacion = tiempo;
            completados++;
        } else {
            if (nivel < 2)
                colas[nivel+1].push(i);
            else
                colas[nivel].push(i);
        }
    }

    imprimir_resultados("FB", procesos, timeline);
}

// ---------------- MAIN ----------------

int main() {
    srand(time(0));

    for (int ronda = 1; ronda <= 5; ronda++) {
        cout << "- Ronda " << ronda << ":\n";

        vector<Proceso> procesos;
        int n = 5;

        for (int i = 0; i < n; i++) {
            Proceso p;
            p.nombre = 'A' + i;
            p.llegada = rand() % 10;
            p.duracion = rand() % 5 + 1;
            p.restante = p.duracion;
            procesos.push_back(p);
        }

        sort(procesos.begin(), procesos.end(),
             [](auto &a, auto &b){ return a.llegada < b.llegada; });

        for (auto &p : procesos) {
            cout << p.nombre << ": " << p.llegada
                 << ", t=" << p.duracion << "; ";
        }
        cout << "\n";

        FCFS(procesos);

        for (auto &p : procesos) p.restante = p.duracion;
        RR(procesos, 1, "RR1");

        for (auto &p : procesos) p.restante = p.duracion;
        RR(procesos, 4, "RR4");

        for (auto &p : procesos) p.restante = p.duracion;
        SPN(procesos);

        for (auto &p : procesos) p.restante = p.duracion;
        FB(procesos);

        cout << "\n";
    }

    return 0;
}