# Tarea 1: Implementación de un intérprete de comandos mínimo (minishell)

**Integrantes:**
- González Martínez Fernando  
- Quezada Olivares Emir






##  Instrucciones de ejecución
El proyecto fue desarrollado en **Python 3**. No requiere de instalación de bibliotecas externas, ya que utiliza módulos de la biblioteca estándar de Python (`os`, `signal`, `sys`, `time`, `shlex` y `readline`).

Para ejecutar el minishell, dentro de una terminal en el directorio donde se encuentre el programa, se deberá ejecutar:


```bash
python3 shell.py
```

**Controles básicos:**
* Para salir del intérprete, se deberá escribir el comando interno `exit` o presiona `Ctrl + D`.
* Puedes usar las flechas del teclado para navegar por el historial de comandos y a través del texto.



## Funcionamiento

### 1. Manejo de señal SIGINT
* Se configuró al proceso padre para ignorar `Ctrl + C`, asegurando que la minishell no se cierre si el usuario intenta interrumpir un comando en ejecución.
* Se implementó la captura de la excepción para manejar el comando `Ctrl + D` y salir limpiamente del flujo de entrada.

### 2. Creación de Procesos y Ejecución
La minishell comienza utilizando `shlex.split()` para parsear la entrada del usuario y almacenarla dentro de una lista. Posteriormente, utiliza `os.fork()` para la creación de un proceso hijo:
* **Proceso Hijo:** Restaura el comportamiento de la señal `SIGINT` (permitiendo interrumpir la ejecución) y utiliza `os.execvp()` para ejecutar el comando solicitado.
* **Proceso Padre:** El padre retorna inmediatamente al bucle principal para seguir leyendo las posteriores entradas del minishell.

### 3. Manejo de procesos hijos
El proceso padre no se bloquea esperando a que el comando termine. En su lugar, continúa ejecutando la interfaz (`input()`) para recibir nuevos comandos libremente. Cuando un proceso hijo termina en segundo plano, el sistema operativo envía la señal `SIGCHLD`. Esta señal interrumpe al padre por una fracción de milisegundo para ejecutar el manejador, el cual elimina definitivamente al proceso hijo usando `os.waitpid(-1, os.WNOHANG)`.




##  Dificultades Encontradas y Soluciones

1. **Condición de Carrera:** Al implementar el modelo asíncrono, el padre regresaba tan rápido a imprimir el prompt `minishell> ` que se sobreponía con la salida de texto del proceso hijo.
   * *Solución:* Se introdujo un pequeño retraso (`time.sleep(0.03)`) en el proceso del padre. 
   Esto permite al hijo procesar e imprimir la información solicitada antes que el padre imprima nuevamente la interfaz.

3. **Movimiento a través de la terminal:**  Al usar las flechas de dirección, la consola imprimía secuencias ANSI (`^[[A`, `^[[D`) en lugar de mover el cursor.
   * *Solución:* Se importó el módulo `readline`, el cual en automático dota al programa de acceso al historial entre entradas, y al desplazamiento entre los textos.