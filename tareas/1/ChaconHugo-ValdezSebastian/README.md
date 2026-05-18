# Mini Shell en Python

## Descripción

Este proyecto implementa un **Mini Shell** en Python que simula el comportamiento básico de una terminal de Linux.
El programa permite al usuario ingresar comandos desde un prompt interactivo y ejecutarlos utilizando llamadas al sistema como **fork()**, **execvp()** y **waitpid()**.

El objetivo principal de este programa es demostrar el funcionamiento de **creación de procesos**, **ejecución de comandos** y **manejo de señales** en sistemas operativos tipo Unix.

---

## Características

El Mini Shell incluye las siguientes funcionalidades:

* Prompt interactivo para ingresar comandos.
* Creación de procesos hijos mediante `fork()`.
* Ejecución de comandos del sistema utilizando `execvp()`.
* Manejo de errores cuando un comando no existe.
* Espera del proceso hijo mediante `waitpid()` para evitar procesos zombie.
* Manejo de la señal **Ctrl+C (SIGINT)** para evitar que el shell termine abruptamente.
* Comando interno `exit` o `quit` para salir del shell.

---

## Requisitos

Para ejecutar este programa se necesita:

* Python 3
* Sistema operativo tipo Unix (Linux o MacOS)

---

## Cómo ejecutar el programa

1. Abrir una terminal.
2. Navegar a la carpeta donde se encuentra el archivo `minishell.py`.

```bash
cd ruta/de/la/carpeta
```

3. Ejecutar el programa:

```bash
python3 minishell.py
```

---

## Ejemplo de uso

Al ejecutar el programa se mostrará el siguiente prompt:

```
--- Bienvenido al Mini-Shell Sistop 2026-2 ---
mi_minishel$
```

El usuario puede ejecutar comandos del sistema como:

```
mi_minishel$ ls
mi_minishel$ pwd
mi_minishel$ whoami
```

Para salir del shell:

```
mi_minishel$ exit
```

---

## Conceptos de Sistemas Operativos utilizados

Este programa utiliza varios conceptos importantes de los sistemas operativos:

### fork()

Crea un proceso hijo duplicando el proceso actual.

### execvp()

Reemplaza el proceso hijo con el programa que el usuario desea ejecutar.

### waitpid()

Permite que el proceso padre espere a que el proceso hijo termine, evitando procesos **zombie**.

### Manejo de señales

Se implementa un manejador para SIGINT (Ctrl+C) que evita que el shell termine abruptamente.

---

## Estructura general del programa

El flujo general del programa es el siguiente:

1. Mostrar un prompt al usuario.
2. Leer el comando ingresado.
3. Separar el comando y sus argumentos.
4. Crear un proceso hijo con `fork()`.
5. El proceso hijo ejecuta el comando con `execvp()`.
6. El proceso padre espera a que el hijo termine.

---

## Dificultades durante el desarrollo

Durante el desarrollo del programa nos encontramos con algunos problemas principalmente relacionados con la implementación práctica del shell.

Uno de los inconvenientes que tuvimos fue que algunos comandos no se ejecutaban correctamente, incluso cuando existían en el sistema. Esto ocurrió porque inicialmente no estábamos separando correctamente el comando y sus argumentos al procesar la entrada del usuario.

También tuvimos que ajustar la forma en la que se limpiaba la entrada del usuario, ya que si el usuario presionaba Enter sin escribir nada, el programa intentaba ejecutar un comando vacío, lo que provocaba errores. Para solucionarlo agregamos una verificación para ignorar entradas vacías.

Otro problema que encontramos fue que cuando un comando no existía, el programa mostraba un error poco claro o terminaba el proceso hijo sin informar correctamente al usuario. Por esta razón agregamos manejo de excepciones para capturar el error y mostrar un mensaje más claro.

Además, durante las pruebas notamos que algunos errores dentro del proceso hijo podían provocar comportamientos inesperados, por lo que fue necesario agregar un manejo de excepciones más general para evitar que el shell se detuviera.

Finalmente, también tuvimos que ajustar el comportamiento del programa para que el shell continuara funcionando después de ejecutar un comando, asegurándonos de que el ciclo principal siguiera activo después de cada ejecución.

---

## Autores

Chacon Hugo
Valdez Sebastian

Materia: **Sistemas Operativos**
Semestre: **Sistop 2026-2**
