#include <stdio.h>

int main() {
    char nombre[50];

    printf("Ingresa tu nombre:\n");
    scanf("%49s", nombre); 
    
    printf("Hola %s\n", nombre);
    return 0;
}
