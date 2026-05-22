#include <stdio.h> 
#include <stdlib.h>
#include <pthread.h>
#include <semaphore.h>
#include <unistd.h>
#include <time.h>

#define NUM_ALUMNOS 6
#define NUM_SILLAS 3
#define MAX_DUDAS 3
#define TAM_COLA (NUM_ALUMNOS * MAX_DUDAS)

// semaforos principales
sem_t sillas;        // controla las sillas disponibles
sem_t hayAlumnos;    // avisa al asesor que hay alguien
sem_t mutexCola;     // protege la cola

// cola de espera
int cola[TAM_COLA];
int frente = 0, fin = 0, enCola = 0;

// semaforos por alumno
sem_t semAlumno[NUM_ALUMNOS];
sem_t semFin[NUM_ALUMNOS];

// datos
int dudas[NUM_ALUMNOS];
int terminados = 0;
int parar = 0;

// mutex para proteger dudas
pthread_mutex_t mutexDudas = PTHREAD_MUTEX_INITIALIZER;

// meter alumno a la cola
int encolar(int x) {
    if (enCola >= TAM_COLA) return -1;
    cola[fin] = x;
    fin = (fin + 1) % TAM_COLA;
    enCola++;
    return 0;
}

// sacar alumno de la cola
int desencolar() {
    if (enCola == 0) return -1;
    int x = cola[frente];
    frente = (frente + 1) % TAM_COLA;
    enCola--;
    return x;
}

void* alumno(void* arg) {
    int id = *(int*)arg;
    unsigned int semilla = (unsigned int)time(NULL) + id * 37;

    while (1) {
        // ver cuantas dudas le quedan
        pthread_mutex_lock(&mutexDudas);
        int misDudas = dudas[id];
        pthread_mutex_unlock(&mutexDudas);

        if (misDudas <= 0) break;

        usleep((rand_r(&semilla) % 2000 + 500) * 1000);

        printf("Alumno %d llega (%d dudas)\n", id, misDudas);

        // intenta agarrar una silla
        if (sem_trywait(&sillas) == 0) {
            printf("Alumno %d se sienta\n", id);

            // entra a la cola
            sem_wait(&mutexCola);
            encolar(id);
            sem_post(&mutexCola);

            // avisa al asesor
            sem_post(&hayAlumnos);

            // espera turno
            sem_wait(&semAlumno[id]);

            // libera la silla cuando pasa
            sem_post(&sillas);

            printf("Alumno %d preguntando...\n", id);
            usleep((rand_r(&semilla) % 1500 + 500) * 1000);
            printf("Alumno %d termina\n", id);

            // reduce sus dudas
            pthread_mutex_lock(&mutexDudas);
            dudas[id]--;
            pthread_mutex_unlock(&mutexDudas);

            // avisa que ya termino
            sem_post(&semFin[id]);

        } else {
            // no hay silla
            printf("Alumno %d no encontro silla, regresa\n", id);
            usleep((rand_r(&semilla) % 1000 + 500) * 1000);
        }
    }

    printf("Alumno %d ya termino\n", id);

    // contar terminados
    sem_wait(&mutexCola);
    terminados++;
    sem_post(&mutexCola);

    return NULL;
}

void* asesor(void* arg) {
    while (!parar) {
        printf("\nAsesor esperando alumnos...\n");

        // espera a que llegue alguien
        sem_wait(&hayAlumnos);
        if (parar) break;

        // toma siguiente de la cola
        sem_wait(&mutexCola);
        int sig = desencolar();
        sem_post(&mutexCola);

        if (sig != -1) {
            printf("Asesor atiende a %d\n", sig);

            // deja pasar al alumno
            sem_post(&semAlumno[sig]);

            // espera a que termine
            sem_wait(&semFin[sig]);

            printf("Asesor termina con %d\n", sig);
        }
    }

    printf("Asesor termina\n");
    return NULL;
}

void* reporte(void* arg) {
    while (!parar) {
        sleep(4);
        if (parar) break;

        // leer estado actual
        sem_wait(&mutexCola);
        int formados = enCola;
        int term = terminados;
        sem_post(&mutexCola);

        pthread_mutex_lock(&mutexDudas);

        printf("\nReporte:\n");
        printf("En cola: %d\n", formados);
        printf("Terminados: %d/%d\n", term, NUM_ALUMNOS);

        printf("Dudas: ");
        for (int i = 0; i < NUM_ALUMNOS; i++) {
            printf("[%d:%d] ", i, dudas[i]);
        }
        printf("\n\n");

        pthread_mutex_unlock(&mutexDudas);
    }

    return NULL;
}

int main() {
    srand(time(NULL));

    pthread_t th_alumnos[NUM_ALUMNOS];
    pthread_t th_asesor, th_reporte;
    int ids[NUM_ALUMNOS];

    printf("Simulacion alumnos y asesor\n\n");

    // inicializar semaforos
    sem_init(&sillas, 0, NUM_SILLAS);
    sem_init(&hayAlumnos, 0, 0);
    sem_init(&mutexCola, 0, 1);

    for (int i = 0; i < NUM_ALUMNOS; i++) {
        sem_init(&semAlumno[i], 0, 0);
        sem_init(&semFin[i], 0, 0);
        dudas[i] = rand() % MAX_DUDAS + 1;
        ids[i] = i;
    }

    // crear hilos
    pthread_create(&th_asesor, NULL, asesor, NULL);
    pthread_create(&th_reporte, NULL, reporte, NULL);

    for (int i = 0; i < NUM_ALUMNOS; i++) {
        pthread_create(&th_alumnos[i], NULL, alumno, &ids[i]);
    }

    // esperar alumnos
    for (int i = 0; i < NUM_ALUMNOS; i++) {
        pthread_join(th_alumnos[i], NULL);
    }

    printf("\nTodos los alumnos terminaron\n");

    // terminar programa
    parar = 1;
    sem_post(&hayAlumnos);

    pthread_join(th_asesor, NULL);
    pthread_join(th_reporte, NULL);

    return 0;
}
