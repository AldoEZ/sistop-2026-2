# Mini Shell en C -> shAI

Este proyecto consiste en una **mini shell desarrollada en lenguaje C para sistemas Unix/Linux**.
La shell permite ejecutar comandos del sistema, cambiar de directorio y manejar señales como `Ctrl+C`.

El programa utiliza llamadas al sistema como `fork()`, `execvp()` y `waitpid()` para crear y gestionar procesos.

---

## Características

* Ejecución de comandos del sistema
* Uso de procesos hijo con `fork()`
* Ejecución de comandos con `execvp()`
* Comando interno `cd` para cambiar de directorio
* Comando `exit` para salir de la shell
* Manejo de `Ctrl+C` mediante señales (`SIGINT`)
* Prompt que muestra el directorio actual

---

## Requisitos

Para compilar y ejecutar el programa necesitas:

* Sistema operativo Linux o Unix
* Compilador GCC
* Biblioteca `readline`

---

## Compilación

Compila el programa con el siguiente comando:

```bash
gcc shAI.c -o shAI -lreadline
```

---

## Ejecución

Después de compilar, ejecuta el programa con:

```bash
./shell
```

La shell mostrará el directorio actual seguido de un símbolo como prompt.

Ejemplo:

```
/home/usuario ♥
```

---

## Uso

Dentro de la shell puedes ejecutar comandos normales del sistema, por ejemplo:

```
ls
pwd
cd dir
cat archivo.txt
```

También puedes usar los siguientes comandos internos:

### Cambiar directorio

```
cd carpeta
```

### Salir de la shell

```
exit
```

---

## Funcionamiento del programa

El programa sigue los siguientes pasos:

1. Muestra el directorio actual como prompt.
2. Lee el comando ingresado por el usuario.
3. Divide la entrada en argumentos.
4. Crea un proceso hijo con `fork()`.
5. El proceso hijo ejecuta el comando usando `execvp()`.
6. El proceso padre espera a que el hijo termine usando `waitpid()`.

---

## Estructura del código

El programa está compuesto por las siguientes funciones principales:

* `main()`
  Controla el ciclo principal de la shell.

* `parsearEntrada()`
  Divide la entrada del usuario en argumentos separados por espacios.

* `configurarInicioSigintStruct()`
  Configura el manejo de la señal `SIGINT` para la shell.

* `configurarHijoSigintStruct()`
  Configura el manejo de señales en el proceso hijo.

* `sigint_handler()`
  Maneja la señal `Ctrl+C` para evitar que la shell se cierre.

* `getCWD()`
  Obtiene el directorio actual para mostrarlo en el prompt.

---

---

## Autores

* Campos Cortes Isaac
* Martínez Pérez Alejandro

---
