# Tarea 2: Ejercicios de Sincronización (Alumnos y Asesor)
**Autores:** Adrián Arzate y David Diaz

## Instrucciones de ejecución

### Si usas Windows
Instala Python 3, guarda el archivo `alumnos_y_asesor.py` en una carpeta y ejecútalo desde la terminal con:

```bash
python alumnos_y_asesor.py
```

### Si usas Linux/Unix
Asegúrate de estar en el directorio donde guardaste el archivo y ejecuta:

```bash
python3 alumnos_y_asesor.py
```

## Breve explicación del diseño
El programa está escrito en Python y usa `threading` para simular la interacción entre varios alumnos y un profesor durante el horario de asesoría.

Se implementan dos tipos de hilos:
- `Alumno`, que representa a cada estudiante
- `Profesor`, que atiende dudas de manera continua

Se usa un semáforo para limitar el número de alumnos dentro del cubículo según el número de sillas disponibles.

Además, se usa un `Lock` para controlar el turno y una `Condition` para sincronizar la interacción entre alumno y profesor, de modo que sólo un alumno pueda presentar una duda y recibir respuesta a la vez.

Cada alumno tiene entre 1 y 10 dudas, y entre una duda y otra cede el turno para permitir que otros alumnos sean atendidos.

## Ejemplo de ejecución
```text
El alumno 1 entró al cubiculo
El alumno 1 está resolviendo una duda
El Profesor está resolviendo una duda
El Profesor terminó con una duda
El alumno 2 entró al cubiculo
El alumno 2 está resolviendo una duda
El Profesor está resolviendo una duda
El Profesor terminó con una duda
El alumno 1 resolvio todas sus dudas
El alumno 1 salió del cubiculo
```

## Dificultades encontradas y cómo se resolvieron
**Coordinación entre alumno y profesor:**  
Se usó un `Lock` junto con una `Condition` para que sólo un alumno sea atendido a la vez y el profesor responda en el momento adecuado.

**Control del número de alumnos dentro del cubículo:**  
Se resolvió con un semáforo inicializado con el número de sillas, evitando que entren más alumnos de los permitidos.

**Ejecución continua del programa:**  
El programa genera alumnos de forma indefinida, por lo que se detiene manualmente con `Ctrl+C`.

## Comentarios finales
La solución modela un escenario clásico de concurrencia con recursos limitados y atención exclusiva, usando mecanismos de sincronización para evitar conflictos entre hilos.
