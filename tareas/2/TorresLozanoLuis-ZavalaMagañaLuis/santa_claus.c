/*
 TORRES LOZANO LUIS
 ZAVALA MAGANA LUIS
 Problema 7: Santa Claus
 ========================
 Mecanismo de sincronizacion:
 mutex + semaforos POSIXc La idea en general es que Santa que puede ser  despertado por dos tipos de clientes: elfos (de 3 en 3) o los 9 renos cuando todos regresan de vacaciones.
 Los renos tienen prioridad sobre los elfos. 
 */

#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <semaphore.h>
#include <unistd.h>
#include <time.h>

/* Configuracion */
#define NUM_RENOS    9
#define NUM_ELFOS   10
#define NUM_VIAJES   3   /* cuantas veces Santa hace su recorrido */

/* Estado compartido  */

/* Contadores que todos los hilos pueden leer/modificar.
   Siempre se acceden bajo el mutex para evitar condiciones de carrera. */
static int renos_listos    = 0;
static int elfos_esperando = 0;
static int viajes_hechos   = 0;

/* Bandera de terminacion: cuando Santa termina sus viajes la pone
   en 0 para que los hilos de elfos sepan que deben salir. */
static volatile int activo = 1;

/* Primitivas de sincronizacion */

/* mutex: protege renos_listos y elfos_esperando.*/
static pthread_mutex_t mutex;

/* sem_santa: Santa se bloquea aqui con sem_wait. Cualquier hilo que quiera despertar a Santa hace sem_post. Iniciado en 0 porque Santa arranca dormido. */
static sem_t sem_santa;

/* sem_reno: los renos se bloquean aqui despues de reportarse. Santa hace sem_post (x9) cuando termina el viaje para  "liberar" a los renos de vuelta al Caribe.*/
static sem_t sem_reno;

/* sem_elfo: los elfos se bloquean aqui esperando la ayuda de Santa. santa hace sem_post (x3) cuando termina de atenderlos.*/
static sem_t sem_elfo;

/* puerta_elfos: este es el semaforo mas importante del lado de los elfos. Se inicializa en 3, lo que significa que solo 3 elfos pueden estar "esperando a Santa" al mismo tiempo.
El elfo numero 4 que llegue se bloqueara hasta que Santa atienda al grupo anterior y libere los 3 lugares.*/
static sem_t puerta_elfos;

static void linea(void)
{
    printf("---------------------------------------------------\n");
}

/* Hilo: Santa Claus*/
void *thread_santa(void *arg)
{
    int i;
    (void)arg;  /* no usamos el argumento, esto evita el warning */

    printf("[SANTA] Santa se queda dormido... Zzz\n");
    linea();

    /* Santa vive en un ciclo: duerme, lo despiertan, trabaja, repite. 
	El ciclo termina cuando ya hizo todos los viajes planeados. */
    while (viajes_hechos < NUM_VIAJES)
    {
/*Santa se bloquea aqui, alguien tiene que hacer sem_post(&sem_santa) para despertarlo. */
        sem_wait(&sem_santa);

/* Al despertar, tomamos el mutex para leer los contadores de forma segura y decidir por que fue despertado.*/
        pthread_mutex_lock(&mutex);

/* Prioridad: primero revisamos si son los renos, aunque un grupo de elfos haya llegado al mismo tiempo, si los 9 renos estan listos, Santa los atiende primero.*/
        if (renos_listos == NUM_RENOS)
        {
            viajes_hechos++;
            printf("\n[SANTA] !Todos los renos llegaron! "
                   "Preparando el trineo... (viaje %d/%d)\n",
                   viajes_hechos, NUM_VIAJES);

/*Resetear el contador antes de soltar el mutex, para que los renos puedan empezar a acumularse de nuevo para el siguiente viaje. */
            renos_listos = 0;
            pthread_mutex_unlock(&mutex);

            sleep(2); /* preparacion del trineo */
            printf("[SANTA] El trineo esta listo, "
                   "saliendo al viaje %d/%d!\n",
                   viajes_hechos, NUM_VIAJES);
            sleep(2); /* duracion del viaje */
            printf("[SANTA] Santa regreso del viaje %d. "
                   "Renos: vuelvan al Caribe!\n", viajes_hechos);
            linea();

/*Liberar a cada reno individualmente. Cada sem_post desbloquea a un reno que estaba esperandoo).*/
            for (i = 0; i < NUM_RENOS; i++)
                sem_post(&sem_reno);
        }
/*Si no son renos, es un grupo de 3 elfos.*/
        else if (elfos_esperando == 3)
        {
            printf("\n[SANTA] Me despierto: 3 elfos necesitan ayuda.\n");

/*Resetear el contador para que el siguiente grupo de 3 elfos pueda formarse.*/
            elfos_esperando = 0;
            pthread_mutex_unlock(&mutex);

            sleep(1);   /*Santa ayuda a elfos*/
            printf("[SANTA] Listo, termine de ayudar a los 3 elfos.\n");
            linea();

/*Desbloquear a los 3 elfos que estaban esperando.*/
            for (i = 0; i < 3; i++)
                sem_post(&sem_elfo);

/* Reabrir la sala de espera: devolver los 3 lugares al semaforo puerta_elfos para que el siguiente grupo de elfos enter. */
            for (i = 0; i < 3; i++)
                sem_post(&puerta_elfos);
        }
        else
        {
/*soltamos el mutex para no dejarlo bloqueado. */
            pthread_mutex_unlock(&mutex);
        }
    }

/* Santa termino todos sus viajes.
Hacemos sem_post para desbloquear a cualquier elfo que pudiera estar bloqueado en los semaforos. */
    activo = 0;
    for (i = 0; i < NUM_ELFOS; i++)
    {
        sem_post(&sem_elfo);
        sem_post(&puerta_elfos);
    }

    printf("\n[SANTA] Ya hice todos mis viajes. "
           "Me voy a descansar. Feliz Navidad!\n");
    return NULL;
}

/*Hilo: Reno*/
void *thread_reno(void *arg)
{
    int id    = *(int *)arg;
    int viaje;

/*Cada reno participa en todos los viajes.*/
    for (viaje = 1; viaje <= NUM_VIAJES; viaje++)
    {
/*Simula las "vacaciones en el Caribe": tiempo aleatorio entre 1 y 3 segundos antes de regresar.*/
        sleep(1 + rand() % 3);

/*Reportarse con Santa: incrementar el contador bajo mutex para que nadie lo modifique al mismo tiempo.*/
        pthread_mutex_lock(&mutex);
        renos_listos++;
        printf("[RENO %2d] Regrese de vacaciones "
               "(renos listos: %d/%d)\n", id, renos_listos, NUM_RENOS);

/*El ultimo reno en llegar es el responsable de despertar a Santa haciendo sem_post. Solo uno lo hace para que Santa no sea despertado 9 veces.*/
        if (renos_listos == NUM_RENOS)
        {
            printf("[RENO %2d] Soy el ultimo. "
                   "Despertando a Santa!\n", id);
            sem_post(&sem_santa);
        }
        pthread_mutex_unlock(&mutex);

/*El reno espera aqui, bloqueado, hasta que Santa termine el viaje.*/
        sem_wait(&sem_reno);
        printf("[RENO %2d] Viaje terminado, "
               "me voy al Caribe de nuevo.\n", id);
    }
    return NULL;
}

/*Hilo: Elfo*/
void *thread_elfo(void *arg)
{
    int id = *(int *)arg;

/* El elfo trabaja indefinidamente hasta que el programa termina. */
    while (activo)
    {
        sleep(1 + rand() % 5);

        if (!activo) break;

/* Intenta entrar a la "sala de espera" de Santa; puerta_elfos empieza en 3, por lo que los primeros 3 elfos pasan sin bloquearse
		El 4to elfo se queda bloqueado aqui hasta que Santa atienda al grupo anterior y libere espacio. */
        sem_wait(&puerta_elfos);

/*Verificar de nuevo por si el programa termina mientras el elfo estaba bloqueado. */
        if (!activo)
        {
            sem_post(&puerta_elfos);
            break;
        }

/*Registrarse en la sala de espera.*/
        pthread_mutex_lock(&mutex);
        elfos_esperando++;
        printf("[ELFO %2d] Tengo un problema! "
               "(elfos esperando: %d/3)\n", id, elfos_esperando);

/*El tercer elfo en llegar despierta a Santa,igual que el ultimo reno.*/
        if (elfos_esperando == 3)
        {
            printf("[ELFO %2d] Somos 3. Despertando a Santa!\n", id);
            sem_post(&sem_santa);
        }
        pthread_mutex_unlock(&mutex);

/*El elfo espera bloqueado aqui hasta que Sant lo atienda*/
        sem_wait(&sem_elfo);

        if (!activo) break;

        printf("[ELFO %2d] Santa me ayudo, vuelvo al trabajo.\n", id);
    }
    return NULL;
}

/*---------------------------MAIN--------------------------*/
int main(void)
{

/*En C89 todas las variables van al inicio del bloque*/
    int i;
    pthread_t hilo_santa;
    pthread_t hilos_renos[NUM_RENOS];
    pthread_t hilos_elfos[NUM_ELFOS];
    int       ids_renos[NUM_RENOS];
    int       ids_elfos[NUM_ELFOS];

    srand((unsigned int)time(NULL));

    linea();
    printf("  Problema de Santa Claus\n");
    printf("  %d renos | %d elfos | %d viajes planeados\n",
           NUM_RENOS, NUM_ELFOS, NUM_VIAJES);
    linea();

    /*Inicializando todas las primitivas antes de crear los hilos.*/
    pthread_mutex_init(&mutex, NULL);
    sem_init(&sem_santa,    0, 0);  /*Santa arranca dormido*/
    sem_init(&sem_reno,     0, 0);  /*renos bloqueados al inicio*/
    sem_init(&sem_elfo,     0, 0);  /*elfos bloqueados al inicio*/
    sem_init(&puerta_elfos, 0, 3);  /*sala de espera: 3 lugares */

    /* Crear primero a Santa para que ya este "dormido"
	antes de que renos y elfos empiecen a llegar. */
    pthread_create(&hilo_santa, NULL, thread_santa, NULL);

    for (i = 0; i < NUM_RENOS; i++)
    {
        ids_renos[i] = i + 1;
        pthread_create(&hilos_renos[i], NULL, thread_reno, &ids_renos[i]);
    }

    for (i = 0; i < NUM_ELFOS; i++)
    {
        ids_elfos[i] = i + 1;
        pthread_create(&hilos_elfos[i], NULL, thread_elfo, &ids_elfos[i]);
    }

    /* Esperar a que todos los hilos terminen antes de salir.*/
    pthread_join(hilo_santa, NULL);

    for (i = 0; i < NUM_RENOS; i++)
        pthread_join(hilos_renos[i], NULL);

    for (i = 0; i < NUM_ELFOS; i++)
        pthread_join(hilos_elfos[i], NULL);
    
    pthread_mutex_destroy(&mutex);
    sem_destroy(&sem_santa);
    sem_destroy(&sem_reno);
    sem_destroy(&sem_elfo);
    sem_destroy(&puerta_elfos);

    linea();
    printf("  Simulacion terminada.\n");
    linea();

    return 0;
}
