# Tarea 3: Comparación de planificadores
**Fecha:** 12 de abril 2026   
**Autores:** Blancas Díaz Isaías y Martínez Sánchez Hans  
**Materia:** Sistemas Operativos  
**Grupo:** 07 
 

## 1. Explicación del diseño
Incluimos los siguientes algoritmos:

- **fcfs (first come first served):** El algoritmo donde el que llega primero se atiende primero de forma completa.

- **spn (shortest process next):** Selecciona al proceso mas corto de los que estan esperando para reducir el tiempo de espera.

-  **round robin (rr1 y rr4):** Divide el tiempo en paquetes (quantum) de 1 y 4 segundos para que todos los procesos avancen de forma justa.

-  **fb (retroalimentacion multinivel):** Implementamos este refinamiento que usa tres colas de prioridad. Si un proceso tarda mucho en terminar, el sistema lo baja de nivel para no estorbar a los procesos más rápidos.

## 2. Lenguaje y Entorno de Desarrollo
* **Lenguaje:** Python 3.X
* **Librerías utilizadas:** `random`: Para la generación y cargas de números aleatorios.
* **Entorno:** El programa fue desarrollado y probado en un entorno Windows, pero es compatible con Linux y macOS.

## 3. Instrucciones de compilación/ejecución
1. Se requiere tener Python instalado en el dispositivo.
2. Abrir una terminal y ubicarse en la direccion o carpeta del programa.
3. ejecutar el comando `python programa.py`


## 4. Ejemplo de ejecución
- Ronda 1:  
  A: 0, t=6; B: 2, t=3; C: 5, t=6; D: 6, t=5; E: 6, t=2  
  FCFS: T=10.6, E=6.2, P=3.16  
  AAAAAABBBCCCCCCDDDDDEE  
  RR1: T=12.2, E=7.8, P=2.87  
  AABABACBDEACDEACDCDCDC  
  RR4: T=11.8, E=7.4, P=3.11  
  AAAABBBAACCCCDDDDEECCD  
  SPN: T=8.8, E=4.4, P=1.97  
  AAAAAAEEBBBDDDDDCCCCCC  
  FB: T=13.2, E=8.8, P=2.97  
  AABBACDECDEBACDACDACDC    
  
  **el programa hará 5 rondas completas y mostrará los resultados de cada una directamente en la pantalla.**

## 5. Dificultades encontradas

Lo mas complicado fue lograr que el esquema visual de letras (el diagrama de gantt) se imprimiera correctamente en algoritmos donde el proceso se interrumpe (como round robin y fb), ya que teniamos que rastrear exactamente en que segundo entraba y salia cada letra. Lo resolvimos usando una cadena de texto que se actualiza en cada ciclo del reloj.