#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define NUM_PROCESOS 5
#define RONDAS 5
#define NUM_COLAS_FB 3 


/*
Estructura de C, que nos ayuda a definir lo que debe tener un Proceso.

id: A
llegada: 0
rafaga: t= x
restante: AAAAAA
fin: usado para calcular el tiempo totol del proceso

*/
typedef struct {
    char id;
    int llegada;
    int rafaga;
    int restante;
    int fin;
} Proceso;


// Funcion para generar un proceso de CPU
void generar_procesos(Proceso p[]) {
    int tiempo_actual = 0;
    for (int i = 0; i < NUM_PROCESOS; i++) {
        p[i].id = 'A' + i;
        p[i].llegada = tiempo_actual;
        p[i].rafaga = (rand() % 7) + 1; 
        p[i].restante = p[i].rafaga;
        tiempo_actual += rand() % 3;   
    }
}

// Funcion para simular el algoritmo First Come First Service (FCFS)
void simular_fcfs(Proceso p[]) {
    int tiempo = 0;
    float sumT = 0, sumE = 0, sumP = 0;
    printf(" -> FCFS: ");

    for (int i = 0; i < NUM_PROCESOS; i++) {
        while (tiempo < p[i].llegada) {
            printf("-");
            tiempo++;
        }
        for (int j = 0; j < p[i].rafaga; j++) {
            printf("%c", p[i].id);
            tiempo++;
        }
        p[i].fin = tiempo;
        // Calculo de metricas, T - tiempo total, E- tiempo de espera, P - penalizacion
        int T = p[i].fin - p[i].llegada;
        int E = T - p[i].rafaga;
        sumT += T; 
        sumE += E; 
        sumP += (float)T / p[i].rafaga; 
    }
    
    printf("\n\tT=%.1f, E=%.1f, P=%.2f\n", sumT / NUM_PROCESOS, sumE / NUM_PROCESOS, sumP / NUM_PROCESOS); // Formato de salida de las metricas de T (tiempo retorno), E (Tiempo de espera) y P (Penalizacion)
}


// Funcion para simular Round Robin
void simular_rr(Proceso p_entrada[], int quantum) {
    int tiempo = 0, completados = 0;
    float sumT = 0, sumE = 0, sumP = 0;
    printf(" -> RR%d:  ", quantum);

    
    Proceso p[NUM_PROCESOS]; // Se realiza una copia de los procesos generados por la funcion generar_procesos(), esto para que los algoritmos no alteren los resultados de los demás y por lo tanto podamos analizar los mismos resultados en cada ronda.
    for (int i = 0; i < NUM_PROCESOS; i++)
        p[i] = p_entrada[i];

   
    int cola[NUM_PROCESOS * 100]; 
    int frente = 0, fin_cola = 0;

  
    for (int i = 0; i < NUM_PROCESOS; i++)
        if (p[i].llegada == 0)
            cola[fin_cola++] = i;

    int en_cola[NUM_PROCESOS]; 
    for (int i = 0; i < NUM_PROCESOS; i++)
        en_cola[i] = (p[i].llegada == 0) ? 1 : 0;

    while (completados < NUM_PROCESOS) {
       
        if (frente == fin_cola) {
            printf("-");
            tiempo++;
            
            for (int i = 0; i < NUM_PROCESOS; i++)
                if (!en_cola[i] && p[i].llegada <= tiempo && p[i].restante > 0) {
                    cola[fin_cola++] = i;
                    en_cola[i] = 1;
                }
            continue;
        }

        int idx = cola[frente++]; 

        int ejecutado = 0;
        while (ejecutado < quantum && p[idx].restante > 0) {
            printf("%c", p[idx].id);
            tiempo++;
            p[idx].restante--;
            ejecutado++;

            
            for (int i = 0; i < NUM_PROCESOS; i++)
                if (!en_cola[i] && p[i].llegada <= tiempo && p[i].restante > 0) {
                    cola[fin_cola++] = i;
                    en_cola[i] = 1;
                }
        }

        if (p[idx].restante == 0) {
            
            p[idx].fin = tiempo;
            int T = p[idx].fin - p[idx].llegada;
            int E = T - p[idx].rafaga;
            sumT += T;
            sumE += E;
            sumP += (float)T / p[idx].rafaga;
            completados++;
        } else {
            
            cola[fin_cola++] = idx;
        }
    }

    printf("\n\tT=%.1f, E=%.1f, P=%.2f\n", sumT / NUM_PROCESOS, sumE / NUM_PROCESOS, sumP / NUM_PROCESOS);
}

// Funcion para simular Short Process Next
void simular_spn(Proceso p_entrada[]) {
    int tiempo = 0, completados = 0;
    float sumT = 0, sumE = 0, sumP = 0;
    printf(" -> SPN:  ");

    
    Proceso p[NUM_PROCESOS];
    int finalizado[NUM_PROCESOS];
    for (int i = 0; i < NUM_PROCESOS; i++) {
        p[i] = p_entrada[i];
        finalizado[i] = 0; 
    }

    while (completados < NUM_PROCESOS) {
        int mejor_i = -1;
        int min_rafaga = 99999; 

        
        for (int i = 0; i < NUM_PROCESOS; i++) {
            if (p[i].llegada <= tiempo && !finalizado[i]) {
                if (p[i].rafaga < min_rafaga) {
                    min_rafaga = p[i].rafaga;
                    mejor_i = i;
                }
            }
        }

        if (mejor_i == -1) {
            printf("-");
            tiempo++;
        } else {

            for (int j = 0; j < p[mejor_i].rafaga; j++) {
                printf("%c", p[mejor_i].id);
                tiempo++;
            }

            p[mejor_i].fin = tiempo;
            finalizado[mejor_i] = 1;
            completados++;

            int T = p[mejor_i].fin - p[mejor_i].llegada;
            int E = T - p[mejor_i].rafaga;
            sumT += T;  
            sumE += E;  
            sumP += (float)T / p[mejor_i].rafaga;
        }
    }
    
    printf("\n\tT=%.1f, E=%.1f, P=%.2f\n", sumT / NUM_PROCESOS, sumE / NUM_PROCESOS, sumP / NUM_PROCESOS);
}


// Funcion para simular FeedBack
void simular_fb(Proceso p_entrada[]) {
    int tiempo = 0, completados = 0;
    float sumT = 0, sumE = 0, sumP = 0;
    printf(" -> FB:   ");

    
    Proceso p[NUM_PROCESOS];
    for (int i = 0; i < NUM_PROCESOS; i++)
        p[i] = p_entrada[i];

    int colas[NUM_COLAS_FB][NUM_PROCESOS * 50];
    int frentes[NUM_COLAS_FB], fines[NUM_COLAS_FB];
    for (int i = 0; i < NUM_COLAS_FB; i++)
        frentes[i] = fines[i] = 0;

    int quantums[NUM_COLAS_FB];
    for (int i = 0; i < NUM_COLAS_FB; i++)
        quantums[i] = 1 << i; // 2^i

    int nivel[NUM_PROCESOS];
    int en_cola[NUM_PROCESOS];
    for (int i = 0; i < NUM_PROCESOS; i++) {
        nivel[i] = 0;
        en_cola[i] = 0;
    }

    for (int i = 0; i < NUM_PROCESOS; i++)
        if (p[i].llegada == 0) {
            colas[0][fines[0]++] = i;
            en_cola[i] = 1;
        }

    while (completados < NUM_PROCESOS) {
        
        int cola_elegida = -1;
        for (int c = 0; c < NUM_COLAS_FB; c++) {
            if (frentes[c] < fines[c]) {
                cola_elegida = c;
                break;
            }
        }

        if (cola_elegida == -1) {
            printf("-");
            tiempo++;
            for (int i = 0; i < NUM_PROCESOS; i++)
                if (!en_cola[i] && p[i].llegada <= tiempo && p[i].restante > 0) {
                    colas[0][fines[0]++] = i;
                    en_cola[i] = 1;
                }
            continue;
        }

        int idx = colas[cola_elegida][frentes[cola_elegida]++];
        int q = quantums[cola_elegida];
        int ejecutado = 0;

        while (ejecutado < q && p[idx].restante > 0) {
            printf("%c", p[idx].id);
            tiempo++;
            p[idx].restante--;
            ejecutado++;

            for (int i = 0; i < NUM_PROCESOS; i++)
                if (!en_cola[i] && p[i].llegada <= tiempo && p[i].restante > 0) {
                    colas[0][fines[0]++] = i;
                    en_cola[i] = 1;
                }
        }

        if (p[idx].restante == 0) {
            
            p[idx].fin = tiempo;
            int T = p[idx].fin - p[idx].llegada;
            int E = T - p[idx].rafaga;
            sumT += T;
            sumE += E;
            sumP += (float)T / p[idx].rafaga;
            completados++;
            en_cola[idx] = 0;
        } else {
            
            en_cola[idx] = 0;
            // Se define siguiente usando un operador ternario (if compacto) el cual determina el siguiente nivel de prioridad de un proceso. Lo cual permite degradar poco a poco a los procesos que no terminan dentro de su quantum.
            int siguiente = (nivel[idx] < NUM_COLAS_FB - 1) ? nivel[idx] + 1 : NUM_COLAS_FB - 1; 
            nivel[idx] = siguiente;
            colas[siguiente][fines[siguiente]++] = idx;
            en_cola[idx] = 1;
        }
    }

    printf("\n\tT=%.1f, E=%.1f, P=%.2f\n", sumT / NUM_PROCESOS, sumE / NUM_PROCESOS, sumP / NUM_PROCESOS);
}


// Funcion para simular Selfish Round Robin o Ronda egoista
void simular_srr(Proceso p_entrada[]) {
    int tiempo = 0, completados = 0;
    float sumT = 0, sumE = 0, sumP = 0;
    printf(" -> SRR:  ");

    
    Proceso p[NUM_PROCESOS];
    for (int i = 0; i < NUM_PROCESOS; i++)
        p[i] = p_entrada[i];

    int estado[NUM_PROCESOS];
    float prioridad[NUM_PROCESOS];
    for (int i = 0; i < NUM_PROCESOS; i++) {
        estado[i] = 0;
        prioridad[i] = 0.0f;
    }

    float a = 1.0f, b = 0.5f;

    int cola_activos[NUM_PROCESOS * 200];
    int frente_a = 0, fin_a = 0;
    int en_cola_activos[NUM_PROCESOS];
    for (int i = 0; i < NUM_PROCESOS; i++) en_cola_activos[i] = 0;

    while (completados < NUM_PROCESOS) {
        
        for (int i = 0; i < NUM_PROCESOS; i++)
            if (estado[i] == 0 && p[i].llegada <= tiempo)
                estado[i] = 1;
                
        int hay_activos = 0;
        float min_prio_activo = 1e9;
        for (int i = 0; i < NUM_PROCESOS; i++)
            if (estado[i] == 2) {
                hay_activos = 1;
                if (prioridad[i] < min_prio_activo)
                    min_prio_activo = prioridad[i];
            }

        for (int i = 0; i < NUM_PROCESOS; i++) {
            if (estado[i] == 1) {
                int promover = 0;
                // La siguiente condicion, regula el momento en que un proceso nuevo puede incorporarse a la cola de ejecución.
                if (!hay_activos) promover = 1;
                else if (prioridad[i] >= min_prio_activo) promover = 1;
                if (promover) {
                    estado[i] = 2;
                    if (!en_cola_activos[i]) {
                        cola_activos[fin_a++] = i;
                        en_cola_activos[i] = 1;
                    }
                    hay_activos = 1;
                    
                    if (prioridad[i] < min_prio_activo)
                        min_prio_activo = prioridad[i];
                }
            }
        }

        if (frente_a == fin_a) {
            printf("-");
            tiempo++;

            for (int i = 0; i < NUM_PROCESOS; i++)
                if (estado[i] == 1) prioridad[i] += b;
            continue;
        }


        int idx = cola_activos[frente_a++];
        printf("%c", p[idx].id);
        tiempo++;
        p[idx].restante--;

        if (p[idx].restante == 0) {
            p[idx].fin = tiempo;
            estado[idx] = 3;
            en_cola_activos[idx] = 0;
            completados++;
            int T = p[idx].fin - p[idx].llegada;
            int E = T - p[idx].rafaga;
            sumT += T;
            sumE += E;
            sumP += (float)T / p[idx].rafaga;
        } else {
            
            en_cola_activos[idx] = 0;
            cola_activos[fin_a++] = idx;
            en_cola_activos[idx] = 1;
        }

        
        for (int i = 0; i < NUM_PROCESOS; i++) {
            if (estado[i] == 2) prioridad[i] += a;  
            if (estado[i] == 1) prioridad[i] += b;  
        }

        
        for (int i = 0; i < NUM_PROCESOS; i++)
            if (estado[i] == 0 && p[i].llegada <= tiempo)
                estado[i] = 1;
    }

    printf("\n\tT=%.1f, E=%.1f, P=%.2f\n", sumT / NUM_PROCESOS, sumE / NUM_PROCESOS, sumP / NUM_PROCESOS);
}

/*

Funcion principal del programa

Se generan siempre 5 rondas de manera aleatoria que ejecutan:

1. FCFS
2. Round Robin 1
3. Round Robin 4
4. Short Process Next
5. FeedBack
6. Selfish Round Robin

Cada una con sus métricas de T, E y P.

*/


int main() {
    srand(time(NULL));
    Proceso procesos[NUM_PROCESOS]; 

    for (int r = 1; r <= RONDAS; r++) {
        printf("\n- Ronda %d:\n", r);
        generar_procesos(procesos); 

        int tot = 0;
        for (int i = 0; i < NUM_PROCESOS; i++) {
            printf("%c: %d, t=%d; ", procesos[i].id, procesos[i].llegada, procesos[i].rafaga);
            tot += procesos[i].rafaga;
        }
        printf("(tot:%d)\n", tot);

        
        simular_fcfs(procesos);       
        simular_rr(procesos, 1);      
        simular_rr(procesos, 4);     
        simular_spn(procesos);        
        simular_fb(procesos);         
        simular_srr(procesos);       
    }
    return 0;
}
