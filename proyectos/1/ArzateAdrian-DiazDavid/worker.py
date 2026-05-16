import threading
import queue

class DiskWorker(threading.Thread):
    """
    Capa Consumidora: Se encarga de procesar las operaciones en tiempo real sobre 
    el archivo fiunamfs.img de manera segura y concurrente.
    """
    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path
        self.task_queue = queue.Queue()
        self.daemon = True
        self.running = True

    def run(self):
        try:
            # Abrimos el archivo simulando el disco.
            # 'r+b' permite leer y escribir en el archivo binario sin truncarlo.
            with open(self.image_path, 'r+b') as disk:
                while self.running:
                    task = self.task_queue.get()
                    
                    # Un None en la cola para apagar el hilo
                    if task is None:
                        self.task_queue.task_done()
                        break
                    
                    self._process_task(disk, task)
                    self.task_queue.task_done()
                    
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo de imagen '{self.image_path}'")
        except Exception as e:
            print(f"Error en el hilo de disco: {e}")

    def _process_task(self, disk, task):
        task_type = task.get('type')
        event = task.get('event')
        
        try:
            # lógica de lectura/escritura de clústeres
            if task_type == 'TEST':
                pass
            
            
            task['success'] = True
        except Exception as e:
            task['success'] = False
            task['error'] = e
        finally:
            # Despertamos al hilo FUSE (Productor) que estaba esperando
            if event:
                event.set()

    def stop(self):
        self.running = False
        # Insertamos un None en la cola para destrabar el self.task_queue.get() bloqueante
        self.task_queue.put(None)
