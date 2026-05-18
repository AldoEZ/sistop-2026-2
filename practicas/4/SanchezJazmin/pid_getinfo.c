#include <stdio.h>
#include <process.h>
//Programa relacionado con la semana
int main(){
	int pid=_getpid();
	printf("Mi pid es_ %d\n",pid);
	FILE *f=fopen("proceso.txt","w");
	if (f==NULL){
		printf("Error al crear el archivo\n");
		return 1;
	}
	fprintf(f, "El pid de este proceso es: %d\n",pid);
	fclose(f);
	printf("Archivo proceso.txt generado\n");
	return 0;
}
