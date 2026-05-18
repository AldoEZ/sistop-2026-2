# Tarea 1: Implementación de un intérprete de comandos mínimo (minishell)

	Tarea planteada: 2026.03.03
	Entrega: 2026.03.10

## **Objetivo**

Implementar un intérprete de comandos básico (shell) que permita al usuario
ejecutar programas del sistema, manejando correctamente la creación de
procesos mediante `fork()`, la ejecución de programas con `exec()` y la
recolección de procesos hijos con señales (`SIGCHLD`).

## **¡Revisión lista!**

Pueden ver ya los [resultados de la revisión de la tarea](./revision.org).

---

### **Especificaciones funcionales**

El programa deberá:

1. **Mostrar un prompt** (por ejemplo, `minishell> `, `>`, `$ `, o el
   símbolo que te guste 😉) y esperar a que el usuario ingrese un comando.

2. **Leer la línea de comandos** ingresada por el usuario, y separar el
   programa de sus argumentos, en caso de haberlos.

3. **Ejecutar el comando** de la siguiente manera:
   - Crear un proceso hijo mediante la llamada al sistema `fork()`
   - En el proceso hijo, utilizar alguna función de la familia a `exec()`
     para reemplazar su imagen con el programa solicitado.
   - El proceso padre debe esperar la finalización del hijo, empleando la
     señal `SIGCHLD` para *recolectarla* de forma asíncrona.

4. **Manejar adecuadamente la señal `SIGCHLD`** :
   - Instalar un manejador para `SIGCHLD` que recolecte los procesos hijos
     que terminan (usando `waitpid()` con la opción `WNOHANG` o su
     equivalente no bloqueante).

5. **Manejar la señal `SIGINT` (Ctrl+C)** :
   - El shell **no debe interrumpir su ejecución** cuando el usuario
     presiona Ctrl+C.
   - La señal `SIGINT` debe ser ignorada por el shell padre, pero permitir
     que los procesos hijos tengan el comportamiento predeterminado
     (terminar).

6. **Permitir la ejecución de comandos simples** (no les estoy pidiendo la
   implementación de un *entorno de programación* como bash). No hace falta
   que manejen *tuberías* (*pipes*), redirecciones ni variables de entorno
   por ahora.

   Un ejemplo de ejecución podría ser: (obviando la salida de los comandos
   solicitados)
   ```
   minishell> ls -l
     (...)
   minishell> ps aux
     (...)
   minishell> echo "Hola mundo"
     (...)
   minishell> exit   → debe terminar el shell
   ```

7. **Manejar el comando interno `exit`** para terminar el shell
   limpiamente.

---

### **Requisitos técnicos y de implementación**

- El programa puede estar escrito en **cualquier lenguaje de programación**
  (C, Python, Java, Go, Rust, etc.), siempre que cumpla con los requisitos
  funcionales.
- Debe ejecutarse correctamente en sistemas Unix/Linux (ya que utiliza
  señales y `fork`).
- Debe manejar correctamente los casos de error (por ejemplo, comando no
  encontrado, `fork()` fallido, etc.) mostrando mensajes de error
  apropiados.
- El código debe estar **bien comentado**, explicando las secciones clave,
  especialmente el manejo de señales y la creación de procesos.
- Debe incluir un archivo `README.md` con:
  - Instrucciones de compilación/ejecución
  - Breve explicación del diseño
  - Ejemplo de ejecución
  - Dificultades encontradas y cómo se resolvieron

---

### **Consideraciones específicas por lenguaje**

**Para Python:**
- Usa el módulo `os` para `fork()`, `execvp()`, `waitpid()`.
- Usa el módulo `signal` para manejar `SIGCHLD` y `SIGINT`.
- Ejemplo base:
  ```python
  import os
  import signal
  import sys

  def sigchld_handler(signum, frame):
      try:
          while True:
              pid, status = os.waitpid(-1, os.WNOHANG)
              if pid == 0:
                  break
              # Procesar terminación del hijo
      except ChildProcessError:
          pass
  ```

**Para C:**
- Usa `fork()`, `execvp()`, `sigaction()`.
- Maneja `SIGCHLD` con `waitpid()` y la opción `WNOHANG`.

**Para otros lenguajes:**
- Investiga las bibliotecas equivalentes para manejo de procesos y señales.

---

### **Entrega**
- La tarea puede realizarse de forma individual, o en equipos de dos
  personas. **Recuerden seguir las normas de nombre de archivo** para su
  entrega (ver la práctica #1).
- La entrega en el repositorio Git deberá contener:
  - Código fuente completo
  - Un archivo `README` con la documentación básica
  - Instrucciones claras para compilar/ejecutar el programa
- Se evaluará:
  - Correcto funcionamiento (60%)
  - Manejo adecuado de señales (20%)
  - Claridad del código y comentarios (10%)
  - Documentación en README (10%)

---

### **Pistas y consideraciones**

- En sistemas Unix, las señales son un mecanismo asíncrono; los manejadores
  deben ser lo más simples posible (idealmente, solo establecer una bandera
  que se revise en el bucle principal).
- El uso de `sigaction()` en C (o `signal.signal()` con banderas apropiadas
  en Python) es más confiable que la función `signal()` tradicional.
- Para parsear la línea de comandos, puedes usar `strtok()` en C,
  `shlex.split()` en Python, o implementar un parser simple manualmente.
- Investiga qué hace exactamente la opción `WNOHANG` (o su equivalente)
  para evitar que `waitpid()` se bloquee.
- Prueba tu shell ejecutando comandos de larga duración (como `sleep 10`) y
  verificando que puedas lanzar otros comandos mientras tanto (aunque sin
  fondo aún, esto demostrará que el manejo de señales funciona).
