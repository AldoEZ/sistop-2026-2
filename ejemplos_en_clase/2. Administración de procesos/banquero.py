#!/usr/bin/python3
#
# Implementación sencilla del Algoritmo del Banquero
#
# Estamos implementando el algoritmo para únicamente _un_ tipo de recursos;
# una implementación “real” tendría que considerar un arreglo de recursos,
# y otorgar únicamente las secuencias seguras _para todos ellos_.
total = 8

procesos = ['A', 'B', 'C']
secuencia = [] # Lo que quiero es _encontrar_ una secuencia segura

reclamo =  {'A': 5, 'B': 5, 'C': 4}
asignado = {'A': 3, 'B': 2, 'C': 2}
libres = total - sum( asignado.values() )

print(f'Iniciamos algoritmo del banquero. Tengo {libres}/{total} recursos.')
while len(procesos) > 0:
    siguiente = None
    for proceso in procesos:
        if reclamo[proceso] - asignado[proceso] <= libres:
            print(f'Podría ser {proceso}. Tengo: {libres}')
            siguiente = proceso

    if siguiente == None:
        raise RuntimeError('¡Estado inseguro!')

    print(f'Asignando: {siguiente}')
    libres += asignado[siguiente]
    procesos.remove(siguiente)
    secuencia.append(siguiente)

print('La secuencia segura encontrada es:')
print(secuencia)



