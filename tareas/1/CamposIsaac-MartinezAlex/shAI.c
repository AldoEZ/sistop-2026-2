/*
 * Proyecto: Mini Shell en C -> shAI (Shell Alex Isaac)
 * Autor: Isaac Campos, Alex Martinez
 * Fecha: 10/03/2026
 * Descripcion: Mini interprete de comandos que hace uso de las
 * funciones fork() y execvp(), ademas de implementar manejadores
 * para las distintas señales que se presentan.
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <readline/readline.h>
#include <sys/wait.h>
#include <signal.h>

/* Prototipos de funciones */
char **parsearEntrada(char *); /* Divide la línea de entrada en tokens */
void sigint_handler(int);      /* Maneja la señal Ctrl+C */
void configurarHijoSigintStruct();  /* Configura el manejo de SIGINT para el hijo */
void configurarInicioSigintStruct();/* Configura el manejo de SIGINT para la shell */
void getCWD(char *, size_t);   /* Obtiene el directorio de trabajo actual */

int main(void){
  char *entrada;      /* Almacena la línea de comando ingresada */
  char **comando;     /* Arreglo de strings para cada argumento del comando */
  pid_t pid_hijo;     /* PID del proceso hijo */
  int status;         /* Estado del proceso hijo */
  char cwd[BUFSIZ];   /* Buffer para mostrar directorio actual */
  char prompt[BUFSIZ];/* Buffer para construir el prompt */

  configurarInicioSigintStruct(); /* Configura manejo de Ctrl+C en la shell */

  while(1){

    getCWD(cwd,sizeof(cwd)); /* Obtiene el directorio actual */
    snprintf(prompt, sizeof(prompt), "%s ♥ ", cwd); /* Construye prompt, es un corazon por nuestra amistad. */
    entrada = readline(prompt); /* Lee la línea de comando del usuario */
 
    if(entrada == NULL){ /* Ctrl+D o fin de archivo */
      printf("byeeeeee\n");
      exit(0);
    }

    comando = parsearEntrada(entrada); /* Separa la entrada en tokens */
	
    if(comando[0]==NULL){ /* Si no hay comando, se salta iteración */
      free(entrada);
      free(comando);
      continue;
    }
	
    if(strcmp(comando[0],"exit") == 0){ /* Comando de salida */
      free(entrada);
      free(comando);
      printf("byeeee\n");
      exit(0);
    }

    if(strcmp(comando[0],"cd") == 0){ /* Cambio de directorio */
      if(chdir(comando[1]) < 0){ /* Si falla, muestra error */
        perror(comando[1]);
      }

      /* Si da tiempo agregar funcionalidad para HOME */
      continue; /* No hace fork si es cd */
    }

    pid_hijo = fork(); /* Crea proceso hijo para ejecutar comando */
	  
    if(pid_hijo < 0){ /* Error en fork */
      perror("Error al ejecutar fork()");
      exit(1);
    }

    if(pid_hijo == 0){ /* Proceso hijo */
      configurarHijoSigintStruct(); /* Manejo de Ctrl+C en el hijo */
      if(execvp(comando[0],comando) < 0){ /* Ejecuta comando */
        perror(comando[0]); /* Si falla, muestra error */
        exit(1);
      }
    } else { /* Proceso padre espera al hijo */
      waitpid(pid_hijo, &status, WUNTRACED);
    }

    free(entrada); /* Libera memoria de entrada y comando */
    free(comando);

  }
  return 0;
}

/* 
 * parsearEntrada
 * Recibe la línea de comando y la separa en tokens usando espacio como delimitador
 * Retorna un arreglo de strings terminado en NULL para usar con execvp
 */
char **parsearEntrada(char *entrada){
  char **comando = malloc(10 * sizeof(char *));
  if(comando == NULL){
    perror("Error al alocar memoria");
    exit(1);
  }
  char *divisor = " ";
  char *parseado;
  int indice = 0;

  parseado  = strtok(entrada, divisor);

  while(parseado != NULL){
    comando[indice] = parseado;
    indice++;
    parseado = strtok(NULL, divisor);
  }

  comando[indice] = NULL; /* Necesario para execvp() */
  return comando;
}

/* Configura la shell para manejar Ctrl+C sin cerrarse */
void configurarInicioSigintStruct(){
  struct sigaction s;
  s.sa_handler = sigint_handler; /* Cuando llegue SIGINT, llama a sigint_handler */
  sigemptyset(&s.sa_mask);       /* No bloquea otras señales mientras se ejecuta */
  s.sa_flags = SA_RESTART;       /* Reinicia funciones interrumpidas (readline, etc) */
  sigaction(SIGINT, &s, NULL);   /* Aplica la configuración a SIGINT */
}

/* Configura el proceso hijo para manejar Ctrl+C */
void configurarHijoSigintStruct(){
  struct sigaction s_hijo;
  s_hijo.sa_handler = sigint_handler; /* Hijos también usan el mismo manejador */
  sigemptyset(&s_hijo.sa_mask);       /* No bloquea otras señales */
  s_hijo.sa_flags = SA_RESTART;       /* Reinicia funciones interrumpidas */
  sigaction(SIGINT, &s_hijo, NULL);   /* Aplica configuración al hijo */
}

/* Función que maneja la señal Ctrl+C
 * Cuando el usuario presiona Ctrl+C, no cierra la shell
 * Solo limpia la línea actual y vuelve a mostrar el prompt
 */
void sigint_handler(int sig){
  printf("\n");                 /* Salto de línea para no sobreescribir prompt */
  rl_on_new_line();             /* Mueve readline a nueva línea */
  rl_replace_line("",0);        /* Borra contenido de la línea actual */
  rl_redisplay();               /* Refresca prompt con línea limpia */
}

/* Obtiene el directorio de trabajo actual y lo guarda en buf */
void getCWD(char *buf, size_t size){
  if(getcwd(buf, size) == NULL){
    perror("getcwd()");
  }
}
