#include <stdio.h>
#include <pthread.h>
#include <semaphore.h>
#include <unistd.h>

#define N 5 // Número de filósofos

sem_t palillos[N]; // Un semáforo por cada palillo

void* filosofo(void* num) {
    int i = *(int*)num;

    while (1) {
        printf("Filósofo %d está pensando...\n", i);
        sleep(1);

        // El último filósofo agarra los palillos al revés para evitar el deadlock
        if (i == N - 1) {
            sem_wait(&palillos[(i + 1) % N]); // Palillo derecho
            sem_wait(&palillos[i]);           // Palillo izquierdo
        } else {
            sem_wait(&palillos[i]);           // Palillo izquierdo
            sem_wait(&palillos[(i + 1) % N]); // Palillo derecho
        }

        printf("Filósofo %d está comiendo... \n", i);
        sleep(2);

        sem_post(&palillos[i]);
        sem_post(&palillos[(i + 1) % N]);

        printf("Filósofo %d termino de comer y solto los palillos.\n", i);
    }
}

int main() {
    pthread_t hilos[N];
    int id[N];

    // Inicializar semaforos
    for (int i = 0; i < N; i++) {
        sem_init(&palillos[i], 0, 1);
        id[i] = i;
    }

    // Crear hilos de filosofos
    for (int i = 0; i < N; i++) {
        pthread_create(&hilos[i], NULL, filosofo, &id[i]);
    }

    // Esperar hilos
    for (int i = 0; i < N; i++) {
        pthread_join(hilos[i], NULL);
    }

    return 0;
}
