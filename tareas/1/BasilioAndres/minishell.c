#define _POSIX_C_SOURCE 200809L //Usando el estandar de Linux:D
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>
#include <signal.h>

#define MAX_LINE 1024
#define MAX_ARGS 100

// Manejador de la señal SIGCHLD para recolectar procesos hijos asíncronamente
void sigchld_handler(int signo) {
    // WNOHANG evita que el padre se bloquee esperando si no hay hijos que recolectar
    while (waitpid(-1, NULL, WNOHANG) > 0);
}

int main() {
    char input[MAX_LINE];
    char *args[MAX_ARGS];

    // Configuración del manejador de señales para SIGCHLD
    struct sigaction sa;
    sa.sa_handler = sigchld_handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = SA_RESTART; // Reiniciar llamadas al sistema interrumpidas
    if (sigaction(SIGCHLD, &sa, NULL) == -1) {
        perror("Error al configurar sigaction");
        exit(EXIT_FAILURE);
    }

    // Ignorar la señal SIGINT (Ctrl+C) en el proceso padre (el shell)
    signal(SIGINT, SIG_IGN);

    while (1) {
        printf("minishell> ");
        fflush(stdout);

        // Leer entrada del usuario; salir si es EOF (Ctrl+D)
        if (fgets(input, sizeof(input), stdin) == NULL) {
            printf("\n");
            break;
        }

        // Eliminar el salto de línea generado por fgets
        input[strcspn(input, "\n")] = 0;

        // Ignorar entradas vacías
        if (strlen(input) == 0) continue;

        // Parsear la entrada en tokens separados por espacio
        int i = 0;
        char *token = strtok(input, " ");
        while (token != NULL) {
            args[i++] = token;
            token = strtok(NULL, " ");
        }
        args[i] = NULL; // execvp requiere que el arreglo termine en NULL

        // Manejo del comando interno 'exit'
        if (strcmp(args[0], "exit") == 0) {
            break;
        }

        // Creación del proceso hijo
        pid_t pid = fork();

        if (pid < 0) {
            perror("Error en fork");
        } else if (pid == 0) {
            // PROCESO HIJO
            // Restaurar el comportamiento por defecto de SIGINT (Ctrl+C) para que el hijo sí pueda ser interrumpido
            signal(SIGINT, SIG_DFL);
            
            // Reemplazar la imagen del proceso con el comando solicitado
            if (execvp(args[0], args) == -1) {
                perror("minishell");
            }
            // Si execvp falla, el proceso hijo debe terminar
            exit(EXIT_FAILURE);
        } else {
            // PROCESO PADRE
            // Esperar específicamente a que el proceso hijo en primer plano termine
            int status;
            waitpid(pid, &status, 0);
        }
    }

    return 0;
}