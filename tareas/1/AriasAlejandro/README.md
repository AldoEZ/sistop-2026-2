# Turtle

Esta guía mostrará el método de ejecución y los comandos que se pueden utilizar en el shell **Turtle**.

---

## Ejecución

Para ejecutar Turtle, se necesita tener instalado **Python 3** y encontrarse en un ordenador con **Sistema Operativo Linux**.

Su ejecución se realiza con el siguiente comando, sobre el directorio en donde se encuentra Turtle:

```bash
python3 turtle.py
```
---

## Uso básico

Al ser un shell basado en Linux, los comandos básicos de este también funcionan.

Este shell admite el uso de variables de entorno mediante el carácter $.


---

### Ejemplo de ejecución
```bash
turtle> sudo apt install tree
[sudo] password for alejandro: 
Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
The following package was automatically installed and is no longer required:
  libllvm17t64
Use 'sudo apt autoremove' to remove it.
The following NEW packages will be installed:
  tree
0 upgraded, 1 newly installed, 0 to remove and 34 not upgraded.
Need to get 47.4 kB of archives.
After this operation, 111 kB of additional disk space will be used.
Get:1 http://mx.archive.ubuntu.com/ubuntu noble-updates/universe amd64 tree amd64 2.1.1-2ubuntu3.24.04.2 [47.4 kB]
Fetched 47.4 kB in 2s (20.4 kB/s) 
Selecting previously unselected package tree.
(Reading database ... 210930 files and directories currently installed.)
Preparing to unpack .../tree_2.1.1-2ubuntu3.24.04.2_amd64.deb ...
Unpacking tree (2.1.1-2ubuntu3.24.04.2) ...
Setting up tree (2.1.1-2ubuntu3.24.04.2) ...
Processing triggers for man-db (2.12.0-4build2) ...
turtle> ls
Desktop  Documents  Downloads  Music  Pictures  Public  snap  Templates  Videos
turtle> whoami
alejandro
turtle>
```
---

## Dificultades encontradas

Una de las mayores dificultades fue el intentar acceder a los comandos y variables del PATH y el no matar la terminal.
Lo resolví leyendo la documentación de la librería os y sys, buscando información en foros y con apoyo de inteligencia artificial.

