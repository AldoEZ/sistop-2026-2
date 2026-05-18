"""
El ejercicio de sincronización que elegimos: Los alumnos y el asesor.

La simulación concurrente la impementamos usando hilos, mutexes, semáforos y una cola FIFO.
Lo cual, según nosotras, cumple con lo establecido en el ejercicio
"""

import argparse #esta librería permite la configuración dinámica de los parámetros del sistema (se pueden ingresar por teclado)
import queue #cola FIFO
import random
import threading
import time
from dataclasses import dataclass, field
from typing import List

class Console:
    #Aquí la impresión tiene que ir ordenada para que la salida no se mezcle entre hilos y se entineda bien el flujo
    def __init__(self) -> None:
        self._lock = threading.Lock()  #asegura que un hilo imprima a la vez
        self._start = time.time() #tiempo inicial

    def log(self, message: str) -> None:
        with self._lock:  #solo un hilo imprime a la vez
            elapsed = time.time() - self._start
            print(f"[{elapsed:7.3f}s] {message}", flush=True)

#esta clase representa a cada alumno 
@dataclass
class Student:
    student_id: int        #ID del alumno
    total_questions: int   #total de preguntas
    start_delay: float     #tiempo antes de llegar
    question_ready: threading.Semaphore = field(default_factory=lambda: threading.Semaphore(0))
    answer_done: threading.Semaphore = field(default_factory=lambda: threading.Semaphore(0))
    questions_done: int = 0   #cuántas preguntas hizo
    entered_at: float | None = None
    finished_at: float | None = None

    @property
    def pending_questions(self) -> int: #preguntas que todavía faltan
        return self.total_questions - self.questions_done

#esta clase es la principal, representa al sistema
class AdvisorOffice:
    def __init__(self, chairs: int, max_questions: int, student_count: int, min_arrival: float, max_arrival: float,
        min_think: float, max_think: float, min_answer: float, max_answer: float,
        seed: int | None = None,
    ) -> None:
        #al momento de ingresar los valores por el teclado, se valida que ninguno de los que se haya puesto sea 0
        if chairs <= 0:
            raise ValueError("el número de sillas debe ser mayor que 0")
        if max_questions <= 0:
            raise ValueError("el máximo de preguntas debe ser mayor que 0")
        if student_count <= 0:
            raise ValueError("el número de estudiantes debe ser mayor que 0")
        if min_arrival < 0 or max_arrival < min_arrival:
            raise ValueError("Rango de llegada inválido")
        if min_think < 0 or max_think < min_think:
            raise ValueError("Rango de pausa entre preguntas inválido")
        if min_answer < 0 or max_answer < min_answer:
            raise ValueError("Rango de atención inválido")

        self.console = Console()
        self.random = random.Random(seed)
        #parámetros del sistema
        self.chairs = chairs
        self.max_questions = max_questions
        self.student_count = student_count
        #tiempos
        self.min_arrival = min_arrival
        self.max_arrival = max_arrival
        self.min_think = min_think
        self.max_think = max_think
        self.min_answer = min_answer
        self.max_answer = max_answer

        self.seats = threading.Semaphore(chairs) #este hilo controla cuántos alumnos pueden estar dentro (sillas)
        self.students_waiting = threading.Semaphore(0)   #cuántos alumnos están esperando (despierta al asesor)
        self.queue_lock = threading.Lock() #protege la cola
        self.stats_lock = threading.Lock() #protege variables 
         #cola FIFO donde se guardan los alumnos
        self.waiting_queue: queue.Queue[Student | None] = queue.Queue()
        #control de terminación
        self.completed_students = 0
        self.student_threads: List[threading.Thread] = []
        self.advisor_thread: threading.Thread | None = None
        self.students: List[Student] = []

#esta función es quien crea los alumnos 
    def create_students(self) -> None:
        for sid in range(1, self.student_count + 1):
            total_questions = self.random.randint(1, self.max_questions)
            start_delay = self.random.uniform(self.min_arrival, self.max_arrival)
            self.students.append(Student(sid, total_questions, start_delay))

#con esta función se mete al alumno a la cola FIFO
    def enqueue_student(self, student: Student) -> None:
        with self.queue_lock:
            self.waiting_queue.put(student)
        self.students_waiting.release() #avisa al asesor
#se saca al alumno de la cola FIFO
    def dequeue_student(self) -> Student | None:
        self.students_waiting.acquire()
        with self.queue_lock:
            return self.waiting_queue.get_nowait()

#hilo que representa al ASESOR
    def advisor(self) -> None:
        self.console.log(
            f"ASESOR  (•◡•): inicia su horario. Hay {self.chairs} sillas disponibles en el cubículo.")

        while True:
            #verificar si ya terminaron todos
            with self.stats_lock:
                if self.completed_students == self.student_count:
                    break

            self.console.log("ASESOR ( ◡́.◡̀): no hay dudas activas; se acuesta a dormir la siesta.")
            student = self.dequeue_student() #espera alumno
            if student is None:
                with self.stats_lock:
                    if self.completed_students == self.student_count:
                        break
                continue

            self.console.log(
                f"ASESOR (◑_◑): despierta porque el alumno {student.student_id} va a presentar su duda.")
            #le da permiso al alumno de hablar
            student.question_ready.release()
            # espera a que termine la pregunta
            student.answer_done.acquire()

        self.console.log("ASESOR  ٩(˘◡˘)۶: terminó el horario de atención. Todos los alumnos fueron atendidos.")


#hilo que representa al ALUMNO
    def student_worker(self, student: Student) -> None:
        time.sleep(student.start_delay) #llega después de cierto tiempo
        self.console.log(
            f"ALUMNO (^◡^ ) {student.student_id}: llega al cubículo con {student.total_questions} "
            f"pregunta(s) en total."
        )
        #intenta sentarse
        self.seats.acquire()
        student.entered_at = time.time()
        self.console.log(
            f"ALUMNO ٩(˘◡˘)۶ {student.student_id}: entra y ocupa una silla. "
            f"Preguntas pendientes: {student.pending_questions}."
        )
          #mientras tenga preguntas
        while student.pending_questions > 0:
            self.enqueue_student(student)# entra a la cola
            student.question_ready.acquire() #espera turno
            #hace la pregunta
            question_number = student.questions_done + 1
            self.console.log(
                f"ALUMNO (╥﹏╥) {student.student_id}: presenta la pregunta {question_number}/"
                f"{student.total_questions}."
            )

            attention_time = self.random.uniform(self.min_answer, self.max_answer)
             #simula tiempo de respuesta
            time.sleep(attention_time)
            student.questions_done += 1

            self.console.log(
                f"ASESOR (>‿◠): responde la pregunta {student.questions_done}/"
                f"{student.total_questions} del alumno {student.student_id}."
            )

            student.answer_done.release() #avisa que terminó

            #si aún tiene dudas, vuelve a intentar
            if student.pending_questions > 0:
                think_time = self.random.uniform(self.min_think, self.max_think)
                self.console.log(
                    f"ALUMNO ヽ(`▭´)ﾉ {student.student_id}: aún tiene dudas; piensa {think_time:.2f}s "
                    "antes de volver a formarse."
                )
                time.sleep(think_time)
        #termina y se va
        student.finished_at = time.time()
        self.console.log(
            f"ALUMNO (ˆ‿ˆԅ) {student.student_id}: resolvió todas sus dudas y sale del cubículo."
        )
        self.seats.release() #libera silla

        #actualizar contador
        with self.stats_lock:
            self.completed_students += 1
            all_done = self.completed_students == self.student_count

        #señal para terminar programa
        if all_done:
            with self.queue_lock:
                self.waiting_queue.put(None)
            self.students_waiting.release()


#Aquí se ejecuta la simulación
    def run(self) -> None:
        self.create_students()
         # iniciar asesor
        self.advisor_thread = threading.Thread(target=self.advisor, name="advisor")
        self.advisor_thread.start()

        #iniciar alumnos
        for student in self.students:
            t = threading.Thread(target=self.student_worker, args=(student,), name=f"student-{student.student_id}")
            self.student_threads.append(t)
            t.start()
        #esperar a que todos terminen
        for t in self.student_threads:
            t.join()

        if self.advisor_thread is not None:
            self.advisor_thread.join()

        self.report()


#Aquí se muestra el reporte final
    def report(self) -> None:
        self.console.log("=" * 72)
        self.console.log("REPORTE FINAL")
        total_system_time = 0.0

        for student in self.students:
            if student.entered_at is None or student.finished_at is None:
                continue
            inside_time = student.finished_at - student.entered_at
            total_system_time += inside_time
            self.console.log(
                f"Alumno {student.student_id}: preguntas={student.total_questions}, "
                f"tiempo dentro del cubículo={inside_time:.3f}s"
            )

        average = total_system_time / len(self.students)
        self.console.log(f"Promedio de tiempo dentro del cubículo: {average:.3f}s")
        self.console.log("Ejecución terminada correctamente.")

#Aquí se leen los argumentos
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Simulación concurrente del problema 'Los alumnos y el asesor'"
    )
    parser.add_argument("--chairs", type=int, default=3, help="Número de sillas dentro del cubículo")
    parser.add_argument("--max-questions", type=int, default=3, help="Máximo de preguntas que puede tener cada alumno")
    parser.add_argument("--students", type=int, default=8, help="Cantidad total de alumnos")
    parser.add_argument("--min-arrival", type=float, default=0.0, help="Llegada mínima (s)")
    parser.add_argument("--max-arrival", type=float, default=2.0, help="Llegada máxima (s)")
    parser.add_argument("--min-think", type=float,default=0.2,help="Pausa mínima entre preguntas del mismo alumno (s)")
    parser.add_argument("--max-think",type=float,default=0.9,help="Pausa máxima entre preguntas del mismo alumno (s)",)
    parser.add_argument("--min-answer",type=float,default=0.3,help="Tiempo mínimo de respuesta del asesor (s)")
    parser.add_argument("--max-answer",type=float,default=1.0,help="Tiempo máximo de respuesta del asesor (s)")
    parser.add_argument("--seed", type=int, default=42, help="Semilla para reproducibilidad")
    return parser.parse_args()

#Programa principal
def main() -> None:
    args = parse_args()
    office = AdvisorOffice(
        chairs=args.chairs,
        max_questions=args.max_questions,
        student_count=args.students,
        min_arrival=args.min_arrival,
        max_arrival=args.max_arrival,
        min_think=args.min_think,
        max_think=args.max_think,
        min_answer=args.min_answer,
        max_answer=args.max_answer,
        seed=args.seed,
    )
    office.run()


if __name__ == "__main__":
    main()
