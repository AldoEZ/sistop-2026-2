import tkinter as tk
from tkinter import messagebox
import sys
import os
import traceback as tb

os.system('cls')

def excepbox(exc_type, exc_value, exc_traceback):
    tb.print_exception(exc_type, exc_value, exc_traceback)
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo(
        "ERROR",
        f"Se encontró un error de tipo {exc_type.__name__} : {exc_value}.\n"
        "Toma una captura de pantalla del error"
    )

sys.excepthook = excepbox

print("Se modifica este programa con esta linea")

root = tk.Tk()
root.withdraw()
messagebox.showinfo("AVISO", "Finalizamos el programa")
