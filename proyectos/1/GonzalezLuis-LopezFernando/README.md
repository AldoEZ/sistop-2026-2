
# Constantes importantes de los requerimientos

```
TAMANO_CLUSTER = 2048
TAMANO_ENTRADA_DIR = 64
CLUSTERS_DIRECTORIO = 8
```


>Refiriendose a línea <>

```python
FORMATO_ENTRADA = "<c15sII6x14s6x14s"
```

- [ ] Poner explicacion

# Comandos útiles durante el desarrollo

## Ver el mapa de memoria con `xxd`
>Durante el desarrollo, antes de implementar cualquier función o clase, inspeccionamos el mapa de memoria del archivo imagen para entender bien lo que estaba pasando con el Superbloque, el directorio, etc

```bash
xxd -s 2048 -l 640 fiunamfs.img
```

>El comando anterior muestra el mapa de memoria del directorio, para las primeras 10 entradas 

**Forma general**
```bash
xxd -s <byte_inicial> -l <cantidad_de_bytes> <archivo_a_leer> | less
```

De esta forma pudimos inspeccionar las entradas de los directorios y con `| less` la parte de datos (que tiende a ser más extensa).

### Explorar el contenido de un archivo de acuerdo a:

Sean:
- $s_v$: tamaño del archivo $v$
- $C_{i_{v}}$: : cluster inicial del archivo $v$

Todos en `bytes`
El rango del contenido de un archivo es: $[C_{i_{v}}, C_{i_{v}} + s_v]$

```bash
xxd -s <c_i_v> -l <s_v> fiunamfs.img | less
```

