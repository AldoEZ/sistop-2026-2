from filesystem import FiUnamFS
import threading

fs = FiUnamFS('fiunamfs.img')

if not fs.validar_fs():
    print('Sistema de archivos invalido.')
    exit()

while True:
    print('\n===== FiUnamFS =====')
    print('1. Listar archivos')
    print('2. Salir')

    opcion = input('Selecciona una opcion: ')

    if opcion == '1':
        hilo = threading.Thread(target=fs.mostrar_archivos)
        hilo.start()
        hilo.join()

    elif opcion == '2':
        break

    else:
        print('Opcion invalida.')
