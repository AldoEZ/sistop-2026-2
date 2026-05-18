#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>

#define NUM_HILOS 4

void* funcion_hilo(void* arg) {
    int id = *(int*)arg;
    printf("Soy el hilo %d\n", id);
    return NULL;
}

int main() {
    pthread_t hilos[NUM_HILOS];
    int ids[NUM_HILOS];

    for (int i = 0; i < NUM_HILOS; i++) {
        ids[i] = i + 1;

        if (pthread_create(&hilos[i], NULL, funcion_hilo, &ids[i]) != 0) {
            perror("Error creando el hilo");
            return 1;
        }
    }

    for (int i = 0; i < NUM_HILOS; i++) {
        pthread_join(hilos[i], NULL);
    }

    return 0;
}