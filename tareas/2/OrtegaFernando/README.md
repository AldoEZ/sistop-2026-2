# Tarea 2 - Ejercicio de sincronizacion: Elevador

Autor: Fernando Ortega
Fecha: 2026-03-26
Materia: Sistemas Operativos

## Problema resuelto

Se implemento el problema del elevador de la Facultad:

- Un hilo representa al elevador.
- Cada persona usuaria del elevador es otro hilo.
- El elevador atiende 5 pisos.
- Cada persona llama al elevador desde un piso y viaja a otro piso.
- Se agrego una interfaz textual en tiempo real con `curses`.

## Lenguaje y entorno

- Lenguaje: Python 3
- Librerias: estandar (threading, condition variables, collections, curses)
- Sistema operativo recomendado: Linux/macOS/Windows con Python instalado

## Como ejecutar

Requisitos:

- Python 3.9 o superior
- Soporte de curses segun sistema operativo:

Linux/GNU (normalmente ya incluido):

```bash
python3 -c "import curses; print('curses OK')"
```

Si falla en Linux/GNU, instalar ncurses y/o la variante de Python con soporte curses (segun distro).

macOS (normalmente ya incluido):

```bash
python3 -c "import curses; print('curses OK')"
```

Windows (instalar dependencia adicional):

```bash
pip install windows-curses
```

Ejecucion basica:

```bash
python elevador_sync.py
```

En Linux/GNU y macOS tambien puedes ejecutar con:

```bash
python3 elevador_sync.py
```

Opciones utiles:

```bash
python elevador_sync.py --personas 30 --tiempo-piso 0.25 --llegada-max 0.6 --seed 20260326
```

Parametros:

- `--personas`: total de usuarios a simular.
- `--tiempo-piso`: tiempo (segundos) para cruzar un piso.
- `--llegada-max`: retardo maximo aleatorio entre llegadas de personas.
- `--seed`: semilla para reproducibilidad.

## Estrategia de sincronizacion

Se usa sincronizacion real con:

- `threading.Lock` para exclusion mutua del estado compartido.
- `threading.Condition` para coordinar eventos (subir, bajar, esperar).

Estado compartido protegido:

- Piso actual del elevador.
- Cola de espera por piso.
- Lista de pasajeros a bordo.
- Estado de cada persona (esperando, a bordo, llego).

Reglas implementadas:

- Capacidad maxima de 5 pasajeros.
- El elevador avanza piso por piso (cruza intermedios).
- Si el elevador pasa por un piso y hay espacio, permite abordar sin importar direccion deseada.
- Los usuarios dentro del elevador son preferidos en la seleccion del siguiente objetivo.

## Refinamiento implementado (anti inanicion)

Se agrego una politica de envejecimiento de solicitudes externas:

- Cada solicitud en espera fuera del elevador acumula antiguedad con el tiempo.
- La seleccion del siguiente piso usa un puntaje:
  - Bonus por destino interno (preferencia por usuarios ya a bordo).
  - Bonus creciente por antiguedad de espera externa.

Con esto se evita que un grupo de pasajeros entre dos pisos monopolice indefinidamente el elevador, porque una solicitud externa muy antigua eventualmente gana prioridad.

## Uso de inteligencia artificial

Para esta entrega use inteligencia artificial como apoyo puntual en la parte de interfaz con `curses`, porque no conocia bien como funcionaba esta libreria y ayuda para mostrar la interfaz estructurandola de la manera que mejor me pareció para representar mejor el problema.

- La IA se uso para comprender la estructura basica de una TUI con `curses` y resolver dudas de implementacion.

## Dudas / mejoras posibles

- La interfaz `curses` puede seguir mejorandose para adaptarse mejor a terminales muy pequenas, es necesario abrir la terminal de un tamaño considerable (casi maxima pantalla).
- Se puede experimentar con diferentes politicas de planificacion para comparar tiempos de espera.
- Una mejora futura es modelar pesos distintos por persona en lugar de peso constante.
