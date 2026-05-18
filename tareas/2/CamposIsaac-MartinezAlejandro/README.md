# Tarea 2 - Problema de sincronización: Alumnos y asesor

Autores: Campos Isaac, Martínez Alejandro
Fecha: 2026-03-26
Materia: Sistemas Operativos

---

## Problema abordado

En esta práctica se desarrolló una simulación del problema de concurrencia "alumnos y asesor":

- Un hilo representa al asesor.
- Cada alumno es modelado como un hilo independiente.
- Los alumnos llegan en tiempos aleatorios con cierto número de dudas.
- Existe un número limitado de sillas para esperar.
- Si un alumno encuentra una silla disponible, espera su turno; de lo contrario, se retira y regresa después.
- El asesor atiende a un alumno a la vez y permanece inactivo cuando no hay alumnos.

---

## Lenguaje y entorno de desarrollo

- Lenguaje: C
- Compilador: gcc
- Bibliotecas utilizadas:
  - pthread
  - semaphore.h
- Sistema operativo: Linux

---

## Cómo ejecutar

### Requisitos

- Compilador de C (por ejemplo gcc)
- Soporte para pthread
- Sistema operativo tipo Unix/Linux

### Compilación

gcc asesor.c -o asesor -pthread

### Ejecución

./asesor

---

## Estrategia de sincronización

El programa utiliza mecanismos de sincronización para coordinar la ejecución de múltiples hilos.

### Mecanismos utilizados

- Semáforos:
  - Control de sillas disponibles (sillas)
  - Aviso de llegada de alumnos (hayAlumnos)
  - Protección de la cola (mutexCola)
  - Sincronización por alumno (semAlumno, semFin)

- Mutex:
  - Protección del acceso a las dudas de cada alumno

### Recursos compartidos

- Cola de espera de alumnos
- Número de alumnos en espera
- Dudas restantes por alumno
- Contador de alumnos que han terminado

### Comportamiento del sistema

- El asesor atiende en orden de llegada.
- Solo un alumno puede ser atendido a la vez.
- Los alumnos liberan su silla cuando pasan con el asesor.
- Cada alumno puede tener varias dudas y regresa hasta resolverlas todas.
- Si no hay sillas disponibles, el alumno se retira y vuelve más tarde.

---

## Monitoreo del sistema

Se implementa un hilo adicional que genera reportes periódicos con información como:

- Cantidad de alumnos en espera
- Número de alumnos que han terminado
- Estado de las dudas de cada alumno

Esto permite observar el comportamiento del sistema en tiempo real.

---

## Uso de inteligencia artificial

Se utilizó inteligencia artificial como apoyo para comprender mejor el uso de hilos y semáforos en C, así como para resolver dudas específicas de implementación.

- Se empleó como herramienta de consulta.
- No se utilizó para generar directamente toda la solución.

---

## Posibles mejoras

- Implementar prioridades entre alumnos.
- Mejorar la política de atención para reducir tiempos de espera.
- Agregar una interfaz visual más clara.
- Permitir modificar parámetros como número de alumnos o sillas en tiempo de ejecución.
