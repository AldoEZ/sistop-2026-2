/*
López Morales Fernando Samuel
Sistemas Operativos | 2026-2
*/
#include <stdio.h>
#include <string.h>
#define MAX_S 50
int main(){
	char cadena[MAX_S];
	printf("Ingresa tu nombre: ");
	fgets(cadena, MAX_S, stdin);
	int tam = -1;
	for(int i = 0; i<MAX_S; i+=1){
		if(cadena[i] == '\0' && tam == -1) tam = i;
	}
	cadena[tam-1] = '\0';
	printf("¡Hola %s!\n", cadena);
	return 0;
}
