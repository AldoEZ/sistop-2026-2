#!/usr/bin/env python3
"""
Programa que demuestra el uso de hilos en Python.
Varios hilos incrementan contadores de forma concurrente y generan
un archivo de reporte con los resultados.

Autor: Fernando Ortega
Fecha: 2026-03-03
"""

import threading
import time
import random

# Archivo de salida que será generado por este programa
ARCHIVO_REPORTE = "reporte_hilos.txt"

# Variables compartidas
contador_global = 0
lock = threading.Lock()
resultados = []

def trabajador(id_hilo, iteraciones):
    """
    Función que ejecuta cada hilo.
    Incrementa un contador global de forma segura usando un lock.
    """
    global contador_global
    
    contador_local = 0
    
    for i in range(iteraciones):
        # Simular algo de trabajo
        time.sleep(random.uniform(0.001, 0.01))
        
        # Sección crítica - acceso al contador global
        with lock:
            contador_global += 1
            contador_local += 1
    
    # Guardar resultado de este hilo
    with lock:
        resultados.append({
            'id': id_hilo,
            'iteraciones': iteraciones,
            'incrementos': contador_local
        })
    
    print(f"Hilo {id_hilo} terminado: {contador_local} incrementos")

def generar_reporte():
    """
    Genera un archivo de reporte con los resultados de la ejecución.
    Este es el archivo autogenerado que debe ser ignorado por git.
    """
    with open(ARCHIVO_REPORTE, 'w', encoding='utf-8') as f:
        f.write("=" * 50 + "\n")
        f.write("REPORTE DE EJECUCIÓN DE HILOS\n")
        f.write("=" * 50 + "\n\n")
        
        f.write(f"Número de hilos ejecutados: {len(resultados)}\n")
        f.write(f"Valor final del contador global: {contador_global}\n\n")
        
        f.write("-" * 50 + "\n")
        f.write("Detalle por hilo:\n")
        f.write("-" * 50 + "\n")
        
        for r in sorted(resultados, key=lambda x: x['id']):
            f.write(f"  Hilo {r['id']}: {r['incrementos']} incrementos "
                    f"(esperados: {r['iteraciones']})\n")
        
        f.write("\n" + "=" * 50 + "\n")
        f.write("Fin del reporte\n")
        f.write("=" * 50 + "\n")
    
    print(f"\nReporte generado en: {ARCHIVO_REPORTE}")

def main():
    """
    Función principal que crea y ejecuta los hilos.
    """
    NUM_HILOS = 5
    ITERACIONES_POR_HILO = 100
    
    print("Demostración de hilos con contador compartido")
    print("-" * 45)
    print(f"Creando {NUM_HILOS} hilos, cada uno con {ITERACIONES_POR_HILO} iteraciones\n")
    
    # Crear los hilos
    hilos = []
    for i in range(NUM_HILOS):
        hilo = threading.Thread(
            target=trabajador,
            args=(i + 1, ITERACIONES_POR_HILO)
        )
        hilos.append(hilo)
    
    # Iniciar todos los hilos
    print("Iniciando hilos...")
    for hilo in hilos:
        hilo.start()
    
    # Esperar a que todos terminen
    for hilo in hilos:
        hilo.join()
    
    print("\nTodos los hilos han terminado.")
    print(f"Contador global final: {contador_global}")
    print(f"Valor esperado: {NUM_HILOS * ITERACIONES_POR_HILO}")
    
    # Generar el archivo de reporte
    generar_reporte()

if __name__ == "__main__":
    main()
