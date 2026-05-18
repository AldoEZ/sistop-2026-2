# Proyecto SO - Micro sistema de archivos multihilos

## Autores

- Adrián Axel Arzate Ríos - **GitHub: @AxlBoy11th**
- David Díaz - **GitHub: @Cuervy117**

## Objetivos

El objetivo principal de este proyecto es implementar un micro sistema de archivos compatible con `FiUnamFS`, utilizando Python y FUSE para permitir que una imagen de disco pueda montarse como un directorio dentro del sistema operativo.

Los objetivos específicos del proyecto son:

1. Leer e interpretar correctamente la estructura interna de una imagen `fiunamfs.img`.
2. Listar los archivos almacenados dentro del sistema de archivos `FiUnamFS`.
3. Copiar archivos desde `FiUnamFS` hacia el sistema operativo anfitrión.
4. Copiar archivos desde el sistema operativo anfitrión hacia `FiUnamFS`.
5. Eliminar archivos almacenados dentro de `FiUnamFS`.
6. Implementar operaciones concurrentes mediante hilos.
7. Utilizar mecanismos de sincronización para evitar inconsistencias al acceder o modificar la imagen del sistema de archivos.
8. Probar el sistema usando comandos comunes de Linux como `ls`, `cp`, `cat` y `rm`.

## Introducción

`FiUnamFS` es un sistema de archivos simple diseñado con fines académicos para comprender cómo se organiza la información dentro de un dispositivo de almacenamiento. En este proyecto, el dispositivo físico se simula mediante un archivo de imagen llamado `fiunamfs.img`.

El sistema de archivos trabaja con una estructura sencilla: un superbloque, un directorio plano y una zona de datos. A partir de esta organización, el programa debe ser capaz de localizar archivos, leer su contenido, escribir nuevos archivos y eliminar entradas existentes.

Para facilitar el uso del sistema, la implementación utiliza FUSE, una herramienta que permite crear sistemas de archivos en espacio de usuario. Gracias a esto, la imagen `fiunamfs.img` puede montarse en una carpeta normal del sistema operativo y manipularse con comandos comunes de terminal.

Este enfoque permite probar el sistema de archivos de forma práctica, ya que el usuario puede interactuar con la imagen como si fuera un directorio real. Además, el proyecto incorpora hilos y mecanismos de sincronización para reforzar los temas vistos en clase sobre sistemas de archivos, concurrencia y administración de procesos.

## Requerimientos del Sistema

### Windows

### Linux

## Explicación del Código

## Pruebas

## Conclusiones
