#include <windows.h>
#include <stdio.h>

int main() {
    STARTUPINFO si;
    PROCESS_INFORMATION pi;

    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);
    ZeroMemory(&pi, sizeof(pi));

    printf("Soy el proceso padre con PID: %lu\n", GetCurrentProcessId());

    // Crear un nuevo proceso (ejemplo: cmd.exe)
    if (CreateProcess(
            "C:\\Windows\\System32\\cmd.exe", // Programa a ejecutar
            NULL,                             // Línea de comandos
            NULL,                             // Seguridad del proceso
            NULL,                             // Seguridad del hilo
            FALSE,                            // Heredar handles
            0,                                // Flags de creación
            NULL,                             // Ambiente
            NULL,                             // Directorio actual
            &si,                              // Info de inicio
            &pi)) {                           // Info del proceso creado

        printf("He creado un hijo con PID: %lu\n", pi.dwProcessId);

        // Esperar a que el hijo termine
        WaitForSingleObject(pi.hProcess, INFINITE);
        printf("El hijo terminó.\n");

        // Cerrar handles
        CloseHandle(pi.hProcess);
        CloseHandle(pi.hThread);
    } else {
        printf("Error al crear el proceso hijo.\n");
    }

    return 0;
}