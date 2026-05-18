#include <stdio.h>

int main(int argc, char *argv[]) {
    if (argc > 1) {
        printf("Hola %s, este es mi saludo personalizado.\n", argv[1]);
    } else {
        printf("Hola, este es mi primer saludo.\n");
    }
    return 0;
}