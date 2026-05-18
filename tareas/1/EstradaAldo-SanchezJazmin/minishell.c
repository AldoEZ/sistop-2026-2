#define _POSIX_C_SOURCE 200809L

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>
#include <signal.h>
#include <errno.h>

#define MAX_INPUT_SIZE 100
#define MAX_ARGS 64

volatile sig_atomic_t fg_done = 0;
volatile sig_atomic_t fg_pid = 0;

/*
funcion que maneja SIGCHLD y recolecta hijos terminados sin bloquear al shell
*/
void sigchld_handler(int sig) {
    int saved_errno = errno;
    pid_t pid;
    
    (void)sig;
    
    while ((pid = waitpid(-1, NULL, WNOHANG)) > 0) {
        if (pid == fg_pid) fg_done = 1;
    }
    
    errno = saved_errno;
}

int main(void) {
    char input[MAX_INPUT_SIZE];
    char *args[MAX_ARGS];
    char *token;
    int i;
    
    struct sigaction sa_chld, sa_int;
    sigset_t block_mask;
    sigset_t prev_mask;
    
    /*
    se configura SIGCHLD para que recolecte los procesos hijos y hacer que el shell 
    ignore SIGINT.
    */
    sa_chld.sa_handler = sigchld_handler;
    sigemptyset(&sa_chld.sa_mask);
    sa_chld.sa_flags = SA_RESTART | SA_NOCLDSTOP;
    
    if (sigaction(SIGCHLD, &sa_chld, NULL) == -1) {
        perror("Error al configurar SIGCHLD");
        exit(EXIT_FAILURE);
    }
    
    sa_int.sa_handler = SIG_IGN;
    sigemptyset(&sa_int.sa_mask);
    sa_int.sa_flags = 0;
    
    if (sigaction(SIGINT, &sa_int, NULL) == -1) {
        perror("Error al configurar SIGINT");
        exit(EXIT_FAILURE);
    }
    
    /*
    genera la máscara que bloqueará SIGCHLD durante la sección crítica.
    */
    sigemptyset(&block_mask);
    sigaddset(&block_mask, SIGCHLD);
    
    /*
    bucle principal del shell que muestra el prompt, lee la entrada y procesa comandos.
    */
    while (1) {
        printf("minishell$ ");
        fflush(stdout);
        
        if (fgets(input, sizeof(input), stdin) == NULL) {
            printf("\n");
            break;
        }
        
        input[strcspn(input, "\n")] = '\0';
        
        if (strcmp(input, "exit") == 0) break;
        
        if (strlen(input) == 0) continue;  
        
        /*
        separacion de la línea en comando y argumentos usando strtok().
        */
        i = 0;
        token = strtok(input, " ");
        
        while (token != NULL && i < MAX_ARGS - 1) {
            args[i++] = token;
            token = strtok(NULL, " ");
        }
        
        args[i] = NULL;
        
        /*
        se bloquea SIGCHLD antes de fork() para evitar carreras entre el padre y el manejador.
        */
        if (sigprocmask(SIG_BLOCK, &block_mask, &prev_mask) == -1) {
            perror("Error al bloquear SIGCHLD");
            continue;
        }
        
        /*
        proceso fork() el cual crea un hijo para ejecutar el comando.
        */
        pid_t pid = fork();
        
        if (pid < 0) {
            perror("Error al crear el proceso");
            sigprocmask(SIG_SETMASK, &prev_mask, NULL);
            continue;
        }
        
        /*
        el proceso hijo restaura SIGINT, quita la máscara heredada y ejecuta el comando con execvp().
        */
        if (pid == 0) {
            struct sigaction sa_default;
            
            sa_default.sa_handler = SIG_DFL;
            sigemptyset(&sa_default.sa_mask);
            sa_default.sa_flags = 0;
            
            if (sigaction(SIGINT, &sa_default, NULL) == -1) {
                perror("Error al configurar SIGINT en el hijo");
                exit(EXIT_FAILURE);
            }
            
            if (sigprocmask(SIG_SETMASK, &prev_mask, NULL) == -1) {
                perror("Error al restaurar la máscara en el hijo");
                exit(EXIT_FAILURE);
            }
            
            execvp(args[0], args);
            perror("Error al ejecutar el comando");
            exit(EXIT_FAILURE);
        }
        
        /*
        el proceso padre registra el hijo en primer plano y espera su terminación con sigsuspend().
        */
        fg_pid = pid;
        fg_done = 0;
        
        while (!fg_done) sigsuspend(&prev_mask);
        
        fg_pid = 0;
        fg_done = 0;
        
        /*
        se restaura la máscara original de señales antes de leer otro comando.
        */
        if (sigprocmask(SIG_SETMASK, &prev_mask, NULL) == -1) {
            perror("Error al restaurar la máscara de señales");
            continue;
        }
    }
    
    return 0;
}
