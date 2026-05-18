#include <stdio.h>
#include <unistd.h>
#include <sys/types.h>
#include <stdlib.h>

int main() {
    pid_t pid_proceso;
    pid_t nvo_pid;

    printf("El PID de este proceso es %d, y el papá es %d\n", getpid(), getppid());

    nvo_pid = fork();

    if (nvo_pid < 0) {
        // Ocurrió un error
        fprintf(stderr, "¡Algo salió mal! ¡El mundo se incendia!\n");
        return 1;
    } 
    else if (nvo_pid == 0) {
        // Soy el proceso hijo
        printf("¡Ya hice mi fork()!\n");
        printf("Soy el proceso hijo (%d). Mi PID es: %d\n", nvo_pid, getpid());
    } 
    else {
        // Soy el proceso padre
        printf("¡Ya hice mi fork()!\n");
        printf("Soy el proceso padre (%d). Mi PID es: %d\n", nvo_pid, getpid());
        
    }

    return 0;
}