#include <stdio.h>
#include <unistd.h>
#include <sys/types.h>
#include <stdlib.h>

int main() {

    pid_t pid, ppid, nvo_pid;

    pid = getpid();
    ppid = getppid();

    printf("El PID de este proceso es %d, y papá es el %d\n", pid, ppid);

    nvo_pid = fork();

    printf("Ya hice mi fork()!\n");

    pid = getpid();

    if (nvo_pid == 0) {
        // Proceso hijo
        printf("Soy el proceso hijo (%d). Mi PID es: %d\n", nvo_pid, pid);
    }
    else if (nvo_pid > 0) {
        // Proceso padre
        printf("Soy el proceso padre (%d). Mi PID es: %d\n", nvo_pid, pid);
    }
    else {
        // Error
        perror("Algo salió mal");
        exit(1);
    }

    return 0;
}