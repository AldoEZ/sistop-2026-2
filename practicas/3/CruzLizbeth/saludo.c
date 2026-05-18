#include <stdio.h>

int main () {
	char nombre [50];

	printf("Hola Mundo\n");
	printf("¿Cuál es tu nombre? ");
	scanf("%49s", nombre);
	printf("Mucho gusto, %s!\n", nombre);

	return 0;
}


