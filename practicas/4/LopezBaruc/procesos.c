#include <stdio.h>
#include <unistd.h>

int main() {
    printf("Ejecutando desde el proceso con PID: %d\n", getpid());
    return 0;
}