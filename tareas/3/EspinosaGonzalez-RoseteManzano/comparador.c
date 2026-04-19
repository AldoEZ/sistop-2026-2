//Tarea3

#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#define N 5  //número de procesos
#define LIM 500  //tamaño maximo del diagrama de gantt

//esta estructura representa un proceso
typedef struct{
  char id;
  int llegada;
  int duracion;
  int restante;
  int fin;
} Proceso;

//copia un arreglo de procesos (para no modificar el original)
void clonar(Proceso a[], Proceso b[], int n){
  int i;
  for(i=0;i<n;i++){
    a[i]=b[i];
    a[i].restante=b[i].duracion;  //reinicia tiempo restante 
    a[i].fin=0;} }         //reinicia tiempo de fin

////ordena procesos por tiempo de llegada (burbuja)
void ordenarLlegada(Proceso p[], int n){
  int i,j;
  Proceso aux;
  for(i=0;i<n-1;i++){
    for(j=i+1;j<n;j++){
      if(p[j].llegada<p[i].llegada){
        aux=p[i];
        p[i]=p[j];
        p[j]=aux;}
      }
    }
  }

//Calcula métricas: T = tiempo de retorno, E = tiempo de espera y P = proporción de penalización 
void sacarMetricas(Proceso p[], int n, float *T, float *E, float *P){
  int i;
  float sumaT=0, sumaE=0, sumaP=0;
  for(i=0;i<n;i++){
    int retorno=p[i].fin-p[i].llegada;
    int espera=retorno-p[i].duracion;
    sumaT+=retorno;
    sumaE+=espera;
    sumaP+=(float)retorno/p[i].duracion; }
  *T=sumaT/n;
  *E=sumaE/n;
  *P=sumaP/n;}

//imprime resultados del algoritmo y diagrama de ejecución
void imprimirResultado(char nombre[], Proceso p[], int n, char gantt[]){
  float T,E,P;
  sacarMetricas(p,n,&T,&E,&P);
  printf("%s -> T=%.2f  E=%.2f  P=%.2f\n",nombre,T,E,P);
  printf("%s\n",gantt);}

//algoritmo FCFS: Primero en llegar, primero en ejecutarse 
void fcfs(Proceso base[], int n){
  Proceso p[N];
  char gantt[LIM];
  int pos=0;
  int t=0;
  int i;
  clonar(p,base,n);
  ordenarLlegada(p,n);
  
  for(i=0;i<n;i++){
    //si no ha llegado el proceso, CPU está inactivo
    while(t<p[i].llegada){
      gantt[pos++]='_';
      t++;}
    // ejecuta todo el proceso
    while(p[i].restante>0){
      gantt[pos++]=p[i].id;
      p[i].restante--;
      t++;}
    p[i].fin=t;}  //guarda el tiempo en que finaliza
  gantt[pos]='\0';
  imprimirResultado("FCFS",p,n,gantt);}

// SPN: ejecuta el proceso más corto disponible 
void spn(Proceso base[], int n){
  Proceso p[N];
  char gantt[LIM];
  int pos=0;
  int t=0;
  int terminados=0;
  int i,mejor;
  clonar(p,base,n);
  while(terminados<n){
    mejor=-1;
    //busca proceso disponible con menor duración
    for(i=0;i<n;i++){
      if(p[i].llegada<=t && p[i].restante>0){
        if(mejor==-1 || p[i].duracion<p[mejor].duracion){
          mejor=i;
        }
      }
    }
    if(mejor==-1){
      gantt[pos++]='_';
      t++;
    }else{
      while(p[mejor].restante>0){
        gantt[pos++]=p[mejor].id;
        p[mejor].restante--;
        t++; }
        p[mejor].fin=t;
        terminados++; } }
      
  gantt[pos]='\0';
  imprimirResultado("SPN",p,n,gantt);}

// Round Robin (planificación por turnos con quantum)
void rr(Proceso base[], int n, int q){
  Proceso p[N];
  char gantt[LIM];
  int pos=0;
  int cola[LIM];
  int ini=0, fin=0;
  int t=0;
  int metidos=0;
  int terminados=0;
  int i,uso;
  clonar(p,base,n);
  ordenarLlegada(p,n);

while(terminados<n){
  //agrega procesos que ya llegaron
  while(metidos<n && p[metidos].llegada<=t){
  cola[fin++]=metidos;
  metidos++; }

  if(ini==fin){
  gantt[pos++]='_';
  t++;
continue; }
i=cola[ini++];
//ejecuta hasta quantum o hasta terminar
uso=(p[i].restante<q)?p[i].restante:q;
while(uso>0){
gantt[pos++]=p[i].id;
p[i].restante--;
  t++;
  uso--;
  //verifica nuevas llegadas durante ejecución
  while(metidos<n && p[metidos].llegada<=t){
    cola[fin++]=metidos;
  metidos++; }   }
//Si no terminó, regresa a la cola
  if(p[i].restante>0){
  cola[fin++]=i;
  }else{
    p[i].fin=t;
    terminados++; }  }
    gantt[pos]='\0';
  if(q==1) imprimirResultado("RR1",p,n,gantt);
    else imprimirResultado("RR4",p,n,gantt);
}

//Retroalimentación multinivel fb (3 colas de prioridad).  Los procesos bajan de nivel si no terminan
void fb(Proceso base[], int n){
  Proceso p[N];
  char gantt[LIM];
  int pos=0;
  //aquí las tres colas 
  int c0[LIM],c1[LIM],c2[LIM];
  int i0=0,f0=0,i1=0,f1=0,i2=0,f2=0; // índices (inicio/fin de cada cola)
  int t=0,metidos=0,terminados=0;
  int i,nivel,q,uso;
  clonar(p,base,n);
  ordenarLlegada(p,n);
  while(terminados<n){
    //Insertar procesos que ya llegaron a la cola de mayor prioridad
    while(metidos<n && p[metidos].llegada<=t){
     c0[f0++]=metidos;
     metidos++;  }
 
  nivel=-1;
  //Seleccionar proceso según prioridad (c0 > c1 > c2)
  if(i0<f0){
    i=c0[i0++];
            
    nivel=0;
    q=1;
    }else if(i1<f1){
      i=c1[i1++];

  nivel=1;
  q=2;
  }else if(i2<f2){
    i=c2[i2++];
    nivel=2;
    q=4;
      }else{
        gantt[pos++]='_';
          t++;
continue; }

//ejecuta hasta q o hasta terminar
uso=(p[i].restante<q)?p[i].restante:q;

 while(uso>0){
  gantt[pos++]=p[i].id;
  p[i].restante--;
  t++;
  uso--;

    //inserta nuevos procesos durante ejecución
     while(metidos<n && p[metidos].llegada<=t){
      c0[f0++]=metidos;
      metidos++; } }
//Si terminó, registrar
if(p[i].restante==0){
  p[i].fin=t;
 terminados++;
 }else{
    //Si no terminó, baja de prioridad
    if(nivel==0) c1[f1++]=i;
    else c2[f2++]=i; }  }
      gantt[pos]='\0';
  imprimirResultado("FB",p,n,gantt);}

//parecido a fb pero con creditos para controlar cuánto ejecuta cada proceso
void srr(Proceso base[], int n){
  Proceso p[N];
  char gantt[LIM];
  int pos=0;
  //Tres colas de prioridad
  int c0[LIM],c1[LIM],c2[LIM];
  int i0=0,f0=0,i1=0,f1=0,i2=0,f2=0;
  int cred[N]; //créditos por proceso
  int t=0,metidos=0,terminados=0;
  int i,nivel;

  clonar(p,base,n);
  ordenarLlegada(p,n);
  //inicializar créditos en 0
  for(i=0;i<n;i++) cred[i]=0;
  while(terminados<n){
    //isertar procesos nuevos en cola 0 con crédito inicial
    while(metidos<n && p[metidos].llegada<=t){
    c0[f0++]=metidos;
    cred[metidos]=1;
    metidos++;    }

  i=-1;
  nivel=-1;
  //Seleccionar proceso por prioridad
    if(i0<f0){
     i=c0[i0++];
     nivel=0;
        }else if(i1<f1){
          i=c1[i1++];
          nivel=1;
 }else if(i2<f2){
            i=c2[i2++];
          nivel=2;
        }else{
 gantt[pos++]='_';
 t++;
    continue; }
        //Si no tiene créditos, se le asignan según nivel
        if(cred[i]<=0){
          if(nivel==0) cred[i]=1;
          else if(nivel==1) cred[i]=2;
            else cred[i]=4;
        }
//ejecuta UNA unidad de tiempo
  gantt[pos++]=p[i].id;
  p[i].restante--;
  cred[i]--;
  t++;

  //verificar nuevas llegadas
  while(metidos<n && p[metidos].llegada<=t){
    c0[f0++]=metidos;
    cred[metidos]=1;
    metidos++; }
 //si terminó, registrar
  if(p[i].restante==0){
    p[i].fin=t;
    terminados++;
        }else 
        //Si aún tiene créditos, se queda en el mismo nivel
        if(cred[i]>0){
          if(nivel==0) c0[f0++]=i;
          else if(nivel==1) c1[f1++]=i;
               else c2[f2++]=i;
              }else{
                //si se quedó sin créditos, baja de nivel
               if(nivel==0){
                cred[i]=2;
                c1[f1++]=i;
              }else{
                cred[i]=4;
                c2[f2++]=i; }
        }}

  gantt[pos]='\0';
  imprimirResultado("SRR",p,n,gantt);}

//genera una ronda random
void generarRonda(Proceso r[], int n){
  int i,llegada=0;
  char letras[5]={'A','B','C','D','E'};

  for(i=0;i<n;i++){
    if(i>0) llegada+=rand()%4; //llegadas crecientes
    r[i].id=letras[i];
    r[i].llegada=llegada;
    r[i].duracion=1+(rand()%8); //duración aleatoria
    r[i].restante=r[i].duracion;
    r[i].fin=0; }
}
////Imprime una ronda completa con todos los algoritmos
void imprimirRonda(Proceso r[], int n, int num){
  int i;
  printf("\nRonda %d\n",num);
  for(i=0;i<n;i++){
    printf("%c -> llegada=%d, t=%d\n",r[i].id,r[i].llegada,r[i].duracion);
    }
   fcfs(r,n);
   rr(r,n,1);
   rr(r,n,4);
   spn(r,n);
   fb(r,n);
   srr(r,n);}

//aqui un ejemplo fijo 
void demo(){
  Proceso r[N];
  r[0].id='A'; r[0].llegada=0;  r[0].duracion=3;  r[0].restante=r[0].duracion;  r[0].fin=0;
  r[1].id='B'; r[1].llegada=1;  r[1].duracion=5;  r[1].restante=r[1].duracion;  r[1].fin=0;
  r[2].id='C'; r[2].llegada=3;  r[2].duracion=2;  r[2].restante=r[2].duracion;  r[2].fin=0;
  r[3].id='D'; r[3].llegada=9;  r[3].duracion=5;  r[3].restante=r[3].duracion;  r[3].fin=0;
  r[4].id='E'; r[4].llegada=12; r[4].duracion=5;  r[4].restante=r[4].duracion;  r[4].fin=0;
  
  printf("Ejemplo fijo\n");
  imprimirRonda(r,N,0);}
  int main(){
    Proceso r[N];
    int i;
    srand((unsigned)time(NULL)); //semilla para aleatorio
    demo(); //Ejecuta ejemplo fijo
    // Ejecuta 5 rondas aleatorias
    for(i=1;i<=5;i++){
    generarRonda(r,N);
    imprimirRonda(r,N,i);
    }return 0;}