/*
Tarea 3 - Comparación de planificadores de procesos
Sistemas Operativos
Integrantes:
 	- Torres Lozano Luis
 	- Zavala Magaña Luis
Lo que hace el programa:
Genera 5 rondas con procesos aleatorios y les aplica cuatro algoritmos de planificacin: FCFS, RR (quantum 1 y 4), SPN y FB (retroalimentación multinivel).
Para cada uno imprime las métricas T, E, P y el diagrama de Gantt.
Compilar: gcc -o compara_planif compara_planif.c
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAXP 5    /*para número de procesos por ronda*/
#define MAXT 200  /*long máx del diagrama de Gantt*/

typedef struct {
	char name;      /*letra identificadora: A, B, C y así*/
	int  llegada;   /*tiempo de llegada*/
	int  duracion;  /*duración total (burst)*/
	int  restante;  /*tiempo que le queda por ejecutar*/
	int  fin;       /*tiempo en que termina*/
} Proceso;

/*Copia el arreglo*/
void copiar(Proceso src[], Proceso dest[]) {
	int i;
	for (i = 0; i < MAXP; i++)
        dest[i] = src[i];
}

/*muestra los procesos de la ronda con su llegada y duración, mas la suma total */
void imprimir_procesos(Proceso p[]) {
	int i, tot = 0;
	for (i = 0; i < MAXP; i++) {
		printf("  %c: %d, t=%d; ", p[i].name, p[i].llegada, p[i].duracion);
		tot += p[i].duracion;
	}
	printf("(tot:%d)\n", tot);
}

/*calcula e imprime T (retorno), E (espera) y P (penalizaciónn) promedio*/
void metricas(Proceso p[]) {
    float T = 0, E = 0, P = 0;
    int i;
    for (i = 0; i < MAXP; i++) {
        int retorno = p[i].fin - p[i].llegada;
        T += retorno;
        E += retorno - p[i].duracion;
        P += (float)retorno / p[i].duracion;
    }
    printf("T=%.2f, E=%.2f, P=%.2f\n", T / MAXP, E / MAXP, P / MAXP);
}

/* 
"First Come First Served": atiende los procesos en orden de llegada, sin interrupciones. El mas sencillo de todos.*/
void fcfs(Proceso p[]) {
	char gantt[MAXT] = "";
	int  tiempo = 0;
	int  i, j;

	for (i = 0; i < MAXP; i++) {
		/*si CPU está libre antes de que llegue el proceso, avanza*/
		if (tiempo < p[i].llegada)
			tiempo = p[i].llegada;

		for (j = 0; j < p[i].duracion; j++) {
			char c[2] = {p[i].name, '\0'};
			strcat(gantt, c);
			tiempo++;
		}
		p[i].fin = tiempo;
	}

	printf("  FCFS: ");
	metricas(p);
	printf("  %s\n", gantt);
}


/*Round Robin con quantum q -> da a cada proceso listo un turno de "q" unidades de tempo y rota en orden en que llegan.*/
void rr(Proceso p[], int q) {
	char gantt[MAXT] = "";
	int  tiempo = 0, completados = 0;
	int  i, j;

	while (completados < MAXP) {
		int progreso = 0;

		for (i = 0; i < MAXP; i++) {
			if (p[i].llegada <= tiempo && p[i].restante > 0) {
				/*ejecuta min(restante, q) unidades*/
				int run = (p[i].restante < q) ? p[i].restante : q;

				for (j = 0; j < run; j++) {
					char c[2] = {p[i].name, '\0'};
					strcat(gantt, c);
					tiempo++;
				}

				p[i].restante -= run;

				if (p[i].restante == 0) {
					p[i].fin = tiempo;
					completados++;
				}
				progreso = 1;
			}
		}

/*si nadie estaba listo, avanzamos el reloj */
		if (!progreso) tiempo++;
	}

	printf("  RR%d: ", q);
	metricas(p);
	printf("  %s\n", gantt);
}
/*Shortest Process Next (no apropiativo) -> en cada desicion escoge el proceso listo con menos tiempo de CPU.*/
void spn(Proceso p[]) {
	char gantt[MAXT] = "";
	int  tiempo = 0, completados = 0;
	int  i, j;

	while (completados < MAXP) {
	/*busca el proceso listo con menor duracion*/
		int idx = -1, menor = 9999;

		for (i = 0; i < MAXP; i++) {
			if (p[i].llegada <= tiempo && p[i].restante > 0) {
				if (p[i].duracion < menor) {
					menor = p[i].duracion;
					idx   = i;
				}
			}
		}

		if (idx == -1) { tiempo++; continue; }

	/* */
		for (j = 0; j < p[idx].duracion; j++) {
			char c[2] = {p[idx].name, '\0'};
			strcat(gantt, c);
			tiempo++;
		}

		p[idx].restante = 0;
		p[idx].fin		= tiempo;
		completados++;
	}

	printf("  SPN: ");
	metricas(p);
	printf("  %s\n", gantt);
}


/* Feedback (retroalimentación multinivel):
Hay varias colas con prioridad decreciente (cola 0 = más alta). El quantum de la cola k es 2^k (1, 2, 4, 8...).
Si un proceso no termina en su quantum, baja a la siguiente cola. Siempre se atiende primero la cola de mayor prioridad con procesos listos.
Es parecido a RR pero penaliza a los procesos largos automáticamente. */
void fb(Proceso p[]) {
	char gantt[MAXT] = "";
	int  tiempo = 0, completados = 0;
	int  cola[MAXP];   /*nivel de cola actual de cada proceso*/
	int  i, j;

/*todos empiezan en la cola de mayor prioridad */
	for (i = 0; i < MAXP; i++) cola[i] = 0;

	while (completados < MAXP) {
	/*elige el proceso listo de mayor prioridad (menor número de cola) */
		int idx = -1, mejor = 9999;

		for (i = 0; i < MAXP; i++) {
			if (p[i].llegada <= tiempo && p[i].restante > 0) {
				if (cola[i] < mejor) {
					mejor = cola[i];
					idx   = i;
				}
			}
		}

		if (idx == -1) { tiempo++; continue; }

	/*quantum = 2^cola*/
		int q = 1;
		for (i = 0; i < cola[idx]; i++) q *= 2;

		int run = (p[idx].restante < q) ? p[idx].restante : q;

		for (j = 0; j < run; j++) {
			char c[2] = {p[idx].name, '\0'};
			strcat(gantt, c);
			tiempo++;
		}

		p[idx].restante -= run;

		if (p[idx].restante == 0) {
			p[idx].fin = tiempo;
			completados++;
		} else {
	/*no termina: baja de prioridad */
			cola[idx]++;
		}
	}

	printf("  FB:  ");
	metricas(p);
	printf("  %s\n", gantt);
}

/* main */
int main() {
	srand(time(NULL));

	int ronda, i, j;

	for (ronda = 1; ronda <= 5; ronda++) {
		printf("\n- Ronda %d:\n", ronda);

		Proceso base[MAXP];

		/*genera procesos con llegada y duración aleatorias*/
		for (i = 0; i < MAXP; i++) {
			base[i].name     = 'A' + i;
			base[i].llegada  = rand() % 10;
			base[i].duracion = 1 + rand() % 6;
			base[i].restante = base[i].duracion;
			base[i].fin      = 0;
		}

		/*ordena por tiempo de llegada (burbuja)*/
		for (i = 0; i < MAXP - 1; i++) {
			for (j = i + 1; j < MAXP; j++) {
				if (base[j].llegada < base[i].llegada) {
					Proceso tmp = base[i];
					base[i]     = base[j];
					base[j]     = tmp;
				}
			}
		}

		imprimir_procesos(base);

		Proceso p[MAXP];

		copiar(base, p);
		for (i = 0; i < MAXP; i++) p[i].restante = p[i].duracion;
		fcfs(p);

		copiar(base, p);
		for (i = 0; i < MAXP; i++) p[i].restante = p[i].duracion;
		rr(p, 1);

		copiar(base, p);
		for (i = 0; i < MAXP; i++) p[i].restante = p[i].duracion;
		rr(p, 4);

		copiar(base, p);
		for (i = 0; i < MAXP; i++) p[i].restante = p[i].duracion;
		spn(p);

		copiar(base, p);
		for (i = 0; i < MAXP; i++) p[i].restante = p[i].duracion;
		fb(p);
	}
return 0;
}
