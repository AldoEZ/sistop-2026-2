Tarea 3: Comparación de planificadores
Alumno: Atilano Velázquez Leonardo
Materia: Sistemas Operativos

Para esta tarea hice un simulador en Python que compara 5 algoritmos: FCFS, Round Robin (con quantum 1 y 4), SPN y uno extra de Colas Múltiples (FB) para el refinamiento de la calificación.

El programa hace 5 rondas. En cada una genera 5 procesos con tiempos de llegada y ráfagas al azar. Luego saca el tiempo de retorno (T), el tiempo perdido (E) y la penalización (P), y también imprime la línea de letras para ver cómo se turnó el CPU. Para ejecutarlo solo hay que correr en la terminal: python compara_planif.py

Sobre el algoritmo de Colas Múltiples (FB):
Para lograr el punto extra armé un despachador con 3 colas distintas:
- Cola 0 (alta): Da un quantum de 1. Aquí entran todos los procesos nuevecitos.
- Cola 1 (media): Da un quantum de 2. Aquí bajan los procesos que no acabaron en la cola 0.
- Cola 2 (baja): Da un quantum de 4. Aquí caen los procesos más largos y ya se quedan dando de vueltas ahí hasta que terminan, porque no hay a dónde bajar más.

Conclusiones de ver los resultados en pantalla:
- SPN casi siempre tiene los mejores promedios de penalización (P) porque saca rápido a los procesos más cortos, aunque a los largos los hace esperar demasiado.
- FCFS depende mucho de la suerte. Si el generador me pone un proceso larguísimo al principio de la ronda, hace que todos los demás tengan tiempos de espera horribles.
- RR1 se ve muy bonito en el esquema de letras porque todos avanzan parejo, pero en números hace que todos los procesos tarden un montón en terminar por completo.
- El de colas múltiples (FB) me pareció el más equilibrado. Atiende rápido a los nuevecitos, pero va empujando a los procesos pesados hacia el final para que no estorben.