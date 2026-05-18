# Tarea 1: Implementación de un intérprete de comandos mínimo (minishell)

## Descripción

Esta tarea consiste en desarrollar un intérprete de comandos mínimo (minishell) en Python para sistemas Unix/Linux

El programa permite:
- Mostrar un prompt y leer comandos del usuario
- Separar el programa y sus argumentos
- Crear procesos hijos con `fork()`
- Ejecutar programas con `execvp()`
- Recolectar procesos hijos terminados mediante la señal `SIGCHLD`
- Ignorar `SIGINT` en el shell padre
- Restaurar el comportamiento normal de `SIGINT` en los procesos hijos
- Manejar el comando interno `exit`

*No se impolementan tuberías, redirecciones ni variables de entorno*

---

## Requisitos
- Python 3
- Sistema operativo Unix/Linux

---

## Instrucciones de ejecución

Ejecutar el programa en bash con:

`pyton3 minishell.py`

