#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h> //Biblioteca para uso de funciones de control de tiempo
#include <stdbool.h>
#include <ncurses.h> //Biblioteca para uso de la interfaz (TUI)
#include <pthread.h> //Biblioteca para manejar hilos

#define NUM_PISOS 5
#define CAPACIDAD 5 //Max capacidad de personas
#define ARRIBA 1
#define ABAJO -1
#define LINEAS 7 //Lineas para mensajes en pantalla

/*
  Seccion de variables globales
*/
int piso_actual = 0;
int direccion_actual = ARRIBA;
int pasajeros_abordo = 0;
int espera[NUM_PISOS] = {0};
int destinos[NUM_PISOS] = {0};
bool puertaAbierta = false;

char mensajes[LINEAS][100];
int contador_mensajes = 0;

/*
  Seccion de inicialización para sincronización
*/
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t cond_pisos[NUM_PISOS];
pthread_cond_t cond_elevador = PTHREAD_COND_INITIALIZER;
pthread_cond_t cond_elevador_wake = PTHREAD_COND_INITIALIZER;

// Función para control de mensajes en pantalla
void mensaje(const char* msj) {
    if (contador_mensajes < LINEAS) {
        strcpy(mensajes[contador_mensajes++], msj);
    } else {
        for(int i = 0; i < LINEAS - 1; i++) {
            strcpy(mensajes[i], mensajes[i+1]);
        }
        strcpy(mensajes[LINEAS - 1], msj);
    }
}

// Funcion para renderizar la interfaz en terminal
void dibujar_tui() {
    erase(); //Borra el contenido en pantalla

    attron(A_BOLD);
    mvprintw(1, 2, "Problema del Elevador");
    attroff(A_BOLD);

    for(int i = NUM_PISOS - 1; i >= 0; i--) {
        int y_pos = 4 + (NUM_PISOS - 1 - i) * 3;

        mvprintw(y_pos, 2, "Piso %d:", i);

        if(piso_actual == i) {
            if(puertaAbierta) {
                mvprintw(y_pos, 10, "< [%d/5] >", pasajeros_abordo);
            } else {
                mvprintw(y_pos, 10, "||[%d/5]||", pasajeros_abordo);
            }
        } else {
            mvprintw(y_pos, 10, "  | |  ");
        }

        mvprintw(y_pos, 25, "Esperando: %d", espera[i]);
        mvprintw(y_pos, 45, "Destinos hacia aqui: %d", destinos[i]);
    }

    mvhline(20, 2, '-', 65);
    mvprintw(21, 2, "Registro de eventos:");

    for(int i = 0; i < contador_mensajes; i++) {
        mvprintw(23 + i, 2, "%s", mensajes[i]);
    }

    refresh(); //Permite actualizar los cambios
}

// Funcion que permite analizar si un usuario quiere bajar o subir en un piso
bool solicitudes() {
    for(int i = 0; i < NUM_PISOS; i++) {
        if (espera[i] > 0 || destinos[i] > 0) return true;
    }
    return false;
}

// Funcion que verifica si el elevador requiere subir
bool solicitud_arriba() {
    for (int i = piso_actual + 1; i < NUM_PISOS; i++) {
        if (espera[i] > 0 || destinos[i] > 0) return true;
    }
    return false;
}

// Funcion que verifica si el elevador requiere bajar
bool solicitud_abajo() {
    for (int i = piso_actual - 1; i >= 0; i--) {
        if (espera[i] > 0 || destinos[i] > 0) return true;
    }
    return false;
}

// Gestiona el movimiento del elevador entre pisos
void update_direction() {
    if (direccion_actual == ARRIBA) {
        if (solicitud_arriba()) direccion_actual = ARRIBA;
        else if (solicitud_abajo()) direccion_actual = ABAJO;
    } else {
        if (solicitud_abajo()) direccion_actual = ABAJO;
        else if (solicitud_arriba()) direccion_actual = ARRIBA;
    }
}

/*
  Hilo del elevador
*/
void* hilo_elevador(void* arg) {
    char msg[100];
    pthread_mutex_lock(&mutex); //Adquirimos el mutex (Sección critica)
    dibujar_tui(); //Llama a la función encargada de la interfaz

    while (1) {
        while (!solicitudes()) {
            sprintf(msg, "[Elevador] Inactivo en piso %d. Durmiendo...", piso_actual);
            mensaje(msg); dibujar_tui(); //Actualiza mensaje e interfaz
            pthread_cond_wait(&cond_elevador_wake, &mutex); //Espera la señal para el piso
        }

        puertaAbierta = true;
        sprintf(msg, "[Elevador] Abriendo puertas en piso %d.", piso_actual);
        mensaje(msg); dibujar_tui(); //Actualiza mensaje e interfaz

        pthread_cond_broadcast(&cond_pisos[piso_actual]); //Se anuncia a los hilos de personas que el elevador alcanzó un piso

        while (destinos[piso_actual] > 0 ||
            (espera[piso_actual] > 0 && pasajeros_abordo < CAPACIDAD)) {
            pthread_mutex_unlock(&mutex); //Liberamos el mutex
        usleep(200000);
        pthread_mutex_lock(&mutex); //Adquirimos el mutex
            }

            puertaAbierta = false;
            sprintf(msg, "[Elevador] Cerrando puertas en piso %d.", piso_actual);
            mensaje(msg); dibujar_tui(); //Actualiza mensaje e interfaz

            if (!solicitudes()) continue;

            update_direction(); // Se actualiza el movimiento del elevador
        if (direccion_actual == ARRIBA) piso_actual++;
        else piso_actual--;

        sprintf(msg, "[Elevador] Viajando hacia el piso %d...", piso_actual);
        mensaje(msg); dibujar_tui(); //Actualiza mensaje e interfaz

        pthread_mutex_unlock(&mutex); //Liberamos el mutex
        sleep(2);
        pthread_mutex_lock(&mutex); //Adquirimos el mutex
    }
    pthread_mutex_unlock(&mutex); //Liberamos el mutex
    return NULL;
}

/*
  Sección para usuarios del elevador (personas)
*/

//Se define la estructura para transferir datos a hilos de los usuarios
typedef struct {
    int id;
    int start_floor;
    int dest_floor;
} PasajerosArgs;

/*
  Hilo de los usuarios
*/
void* hilo_persona(void* arg) {
    PasajerosArgs* p = (PasajerosArgs*)arg; //
    int id = p->id;
    int start = p->start_floor;
    int dest = p->dest_floor;
    char msg[100];

    pthread_mutex_lock(&mutex); //Adquirimos el mutex (Sección critica)

    espera[start]++;
    sprintf(msg, "[Usuario %d] Esperando en piso %d (Destino: %d)", id, start, dest);
    mensaje(msg); dibujar_tui();

    pthread_cond_signal(&cond_elevador_wake); //Despertamos al hilo del elevador por precaución

    while (!(piso_actual == start && puertaAbierta && pasajeros_abordo < CAPACIDAD)) {
        pthread_cond_wait(&cond_pisos[start], &mutex); //Espera a que el elevador llegue a su piso y pueda entrar
    }

    espera[start]--;
    pasajeros_abordo++; //Se aumenta la cantidad de personas en el elevador
    destinos[dest]++; //Se aumenta un destino

    sprintf(msg, "[Usuario %d] Aborda en piso %d.", id, start);
    mensaje(msg); dibujar_tui();

    pthread_cond_signal(&cond_elevador); //Avisa que el elevador se movió

    while (!(piso_actual == dest && puertaAbierta)) {
        pthread_cond_wait(&cond_pisos[dest], &mutex); //Espera a llegar al piso correcto y que pueda salir
    }

    pasajeros_abordo--; //Se disminuye la cantidad de personas en el elevador
    destinos[dest]--; //Se quita un destino

    sprintf(msg, "[Usuario %d] Baja en piso %d. Viaje terminado.", id, dest);
    mensaje(msg); dibujar_tui();

    pthread_cond_signal(&cond_elevador); //Avisa que el elevador se movió

    pthread_mutex_unlock(&mutex); //Se libera el mutex
    free(p); //Se libera la memoria de los args
    return NULL;
}

int main() {
    initscr(); //Inicializa pantalla para interfaz
    cbreak();
    noecho(); //No se imprime lo que escriba el usuario
    curs_set(0); //Oculta cursor

    for (int i = 0; i < NUM_PISOS; i++) {
        pthread_cond_init(&cond_pisos[i], NULL);
    }

    pthread_t elevator;
    pthread_create(&elevator, NULL, hilo_elevador, NULL); //Se crea el hilo del elevador

    // Se establecen rutas de ejemplo
    int test_routes[8][2] = {
        {0, 4}, {0, 3}, {1, 4},
        {4, 0}, {3, 1},
        {2, 0}, {2, 4},
        {1, 2}
    };

    pthread_t passengers[8]; //Se crean 8 usuarios para el elevador (hilos de personas)
    for (int i = 0; i < 8; i++) {
        PasajerosArgs* args = malloc(sizeof(PasajerosArgs));
        args->id = i + 1;
        args->start_floor = test_routes[i][0]; //Se asigna piso inicial
        args->dest_floor = test_routes[i][1]; //Se asigna piso destino
        pthread_create(&passengers[i], NULL, hilo_persona, args);
        sleep(1);
    }

    for (int i = 0; i < 8; i++) {
        pthread_join(passengers[i], NULL); //Espera a que todos los usuarios lleguen a su destino
    }

    pthread_mutex_lock(&mutex); //Adquirimos mutex
    mensaje("Todos los usuarios llegaron a su destino. Presiona cualquier tecla...");
    dibujar_tui();
    pthread_mutex_unlock(&mutex); //Se libera el mutex

    getch(); //Pausa hasta que se presione una tecla
    endwin(); //Finaliza la interfaz y muestra la terminal

    return 0;
}
