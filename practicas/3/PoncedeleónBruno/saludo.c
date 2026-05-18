#include <stdio.h>

char usuario[15];

int main (void){

    printf("\nFavor de ingresar tu usuario\n");
    scanf("%s",&usuario);
    printf("\nHola %s :D\n", usuario);
    return 0;
}
