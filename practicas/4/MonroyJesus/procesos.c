#include <stdio.h>
#include <stdlib.h>

#ifdef _WIN32
  #include <windows.h>
#else
  #include <unistd.h>
  #include <sys/types.h>
  #include <sys/wait.h>
#endif

int main() {
	#ifdef _WIN32
       printf("Hola soy el proceso original que usa este programa. Mi PID en Windows es: %lu\n", GetCurrentProcessId());

       STARTUPINFO si = { sizeof(si) };
       PROCESS_INFORMATION pi;
       char cmd[] = "cmd.exe /c echo Proceso hijo inyectado en Windows.";
       if (CreateProcess(NULL, cmd, NULL, NULL, FALSE, 0, NULL, NULL, &si, &pi)) 
       {
          printf("Se ha creado un proceso hijo exitosamente. Su PID es: %lu\n", pi.dwProcessId);
          WaitForSingleObject(pi.hProcess, INFINITE);
          CloseHandle(pi.hProcess);
          CloseHandle(pi.hThread);
        } 
        else 
        {
          printf("Error al crear proceso en Windows :(\n");
        }
     #else
       printf("Hola soy el proceso original que usa este programa. Mi PID en UNIX/Linux es: %d\n", getpid());

       pid_t pid = fork();

       if (pid == 0) 
       {

          printf("Se utiliza fork para crear un proceso hijo. Su PID es: %d\n", getpid());
          printf("Usando exec() para cambiar de imagen de programa...\n");

          execlp("echo", "echo", "Se ha utilizado exec() exitosamente", NULL);
        } 
        else if (pid > 0) 
        {
          printf("Se ha creado un proceso hijo exitosamente. Su PID es: %d\n", pid);
          wait(NULL);
        } 
        else 
        {
          printf("Error en el fork.\n");
        }
  #endif
     printf("Ejecucion finalizada limpiamente.\n");
     return 0;
  }          
