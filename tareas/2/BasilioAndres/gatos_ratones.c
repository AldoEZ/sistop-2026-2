#include <stdio.h>
#include <pthread.h>
#include <semaphore.h>
#include <unistd.h>
#include <stdlib.h>

#define M_PLATOS 3
#define K_GATOS 5
#define L_RATONES 8

// Semáforos para el control de acceso
sem_t zona_comedor;   // Controla quién tiene el turno
sem_t platos_libres;  // Solo M animales pueden comer a la vez
sem_t mutex_gatos;    // Protege el acceso al contador de gatos
sem_t mutex_ratones;  // Protege el acceso al contador de ratones

int gatos_en_turno = 0;
int ratones_en_turno = 0;

void* hilo_gato(void* arg) {
    int id = *(int*)arg;
    while(1) {
        // Los gatos pasean antes de buscar comida
        sleep(rand() % 3 + 1);

        // El primer gato bloquea la sala para los ratones - entrada
        sem_wait(&mutex_gatos);
        gatos_en_turno++;
        if (gatos_en_turno == 1) sem_wait(&zona_comedor);
        sem_post(&mutex_gatos);

        // Se sienta a comer en uno de los M platos
        sem_wait(&platos_libres);
        printf("Gato %d: Comiendo de un plato. Quedan gatos esperando turno.\n", id);
        sleep(2);
        sem_post(&platos_libres);

        // El último gato libera la sala - salida
        sem_wait(&mutex_gatos);
        gatos_en_turno--;
        if (gatos_en_turno == 0) sem_post(&zona_comedor);
        sem_post(&mutex_gatos);

        // Pausa para evitar inanición de los ratones
        sleep(3); 
    }
}

void* hilo_raton(void* arg) {
    int id = *(int*)arg;
    while(1) {
        sleep(rand() % 2 + 1);

        // El primer ratón bloquea la sala para los gatos - entrada
        sem_wait(&mutex_ratones);
        ratones_en_turno++;
        if (ratones_en_turno == 1) sem_wait(&zona_comedor);
        sem_post(&mutex_ratones);

        // Come de un plato siempre que no haya gatos
        sem_wait(&platos_libres);
        printf("Ratón %d: Comiendo de un plato... ¡Sin gatos a la vista!\n", id);
        sleep(1);
        sem_post(&platos_libres);

        // Salida
        sem_wait(&mutex_ratones);
        ratones_en_turno--;
        if (ratones_en_turno == 0) sem_post(&zona_comedor);
        sem_post(&mutex_ratones);

        sleep(2);
    }
}

int main() {
    pthread_t gatos[K_GATOS], ratones[L_RATONES];
    int ids[K_GATOS + L_RATONES];

    // Inicialización de los semáforos
    sem_init(&zona_comedor, 0, 1);         // La zona está libre al inicio
    sem_init(&platos_libres, 0, M_PLATOS); // Hay M platos disponibles
    sem_init(&mutex_gatos, 0, 1);          // Variable de estado para gatos
    sem_init(&mutex_ratones, 0, 1);        // Variable de estado para ratones

    for(int i = 0; i < K_GATOS; i++) {
        ids[i] = i;
        pthread_create(&gatos[i], NULL, hilo_gato, &ids[i]);
    }
    for(int i = 0; i < L_RATONES; i++) {
        ids[i + K_GATOS] = i;
        pthread_create(&ratones[i], NULL, hilo_raton, &ids[i + K_GATOS]);
    }

    for(int i = 0; i < K_GATOS; i++) pthread_join(gatos[i], NULL);
    
    return 0;
}