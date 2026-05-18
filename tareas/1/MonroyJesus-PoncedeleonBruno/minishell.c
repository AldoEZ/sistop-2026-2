#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>
#include <signal.h>
#include <errno.h>

#define MAX_LINE 1024 // Tamaño maximo de cadena que recibe la minishell
#define MAX_ARGS 64 // Cantidad maxima de argumentos que recibe la minishell

/*
 Manejador de la señal SIGCHLD
*/
void manejar_sigchld(int sig) {
    int saved_errno = errno; // Se guarda el valor de errno para restaurarlo posteriormente

	// WNOHANG se usa para esperar sin que se bloquee la minishell
    while (waitpid(-1, NULL, WNOHANG) > 0); // Cada vez que un proceso hijo termina, se limpia	

    errno = saved_errno; // Se restaura el valor de errno
}

/*
 Se realiza la configuración inicial de señales
*/
void config_signals() {
    struct sigaction sa_chld, sa_int; // Se crean las estructuras para manejar procesos hijos y la señal de interrupcion

    // Manda a manejar SIGCHLD para limpiar el proceso y evitar procesos "zombie"
    sa_chld.sa_handler = manejar_sigchld;
    sigemptyset(&sa_chld.sa_mask);
    // SA_RESTART: Evita que las llamadas fallen al interrumpirse por la señal
    sa_chld.sa_flags = SA_RESTART | SA_NOCLDSTOP;
    if (sigaction(SIGCHLD, &sa_chld, NULL) == -1) {
        perror("Error con la señal SIGCHLD");
        exit(1);
    }

    // Se ignora Ctrl+C (la señal SIGINT)
    sa_int.sa_handler = SIG_IGN;
    sigemptyset(&sa_int.sa_mask);
    sa_int.sa_flags = 0;
    if (sigaction(SIGINT, &sa_int, NULL) == -1) {
        perror("Error con la señal SIGINT");
        exit(1);
    }
}

/*
 Funcion para ejecutar el comando ingresado por el usuario
*/

// Se pasan los comandos ingresados por el usuario a la funcion
void ejecutar_comando(char **args) {
    pid_t pid = fork(); // Se crea un proceso hijo y se almacena su ID (PID)

    if (pid < 0) {
        perror("minishell: fork");
    } else if (pid == 0) {
        signal(SIGINT, SIG_DFL); // Se restaura SIGINT para que el proceso hijo pueda ser interrumpido

        if (execvp(args[0], args) == -1) { // execvp busca el comando en PATH
            fprintf(stderr, "minishell: comando no encontrado: %s\n", args[0]);
        }
        exit(EXIT_FAILURE);
    } else {
        // --- PROCESO PADRE ---
        int status;
        waitpid(pid, &status, 0); // Espera a que termine el proceso hijo creado
    }
}

/*
 Funcion principal del programa
*/
int main() {
    char line[MAX_LINE]; // Se establece el tamaño maximo para la cadena de la minishell
    char *args[MAX_ARGS]; // Se establece la cantidad maxima de caracteres

    config_signals(); // Se realiza la configuracion inicial de señales

    while (1) {
        printf("user@miniShell> "); // Se establece el prompt personalizado
        fflush(stdout);

        if (!fgets(line, MAX_LINE, stdin)) {  // Lee la entrada del usuario
            // Se utiliza Ctrl+D como combinacion para salir del programa (End of file)
            printf("\nSaliendo de la minishell...\n");
            break;
        }

        line[strcspn(line, "\n")] = '\0';

        int i = 0;
        args[i] = strtok(line, " \t\n\r"); // Se divide por palabra la cadena ingresada para los comandos (se parsea)
        
        while (args[i] != NULL && i < MAX_ARGS - 1) {
            args[++i] = strtok(NULL, " \t\n\r");
        }
        args[i] = NULL; // El último elemento debe ser NULL para execvp

        if (args[0] == NULL) continue; // Si no se escribe nada, el programa continua

        if (strcmp(args[0], "exit") == 0) { // En caso de ejecutar exit, se cierra la minishell
            break;
        }

        ejecutar_comando(args); // Llama a la función para ejecutar el comando insertado
    }

    return 0;
}
