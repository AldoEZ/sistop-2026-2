from datetime import datetime

# Archivo autogenerado (no debe subirse)
OUT = "salida.log"

with open(OUT, "w", encoding="utf-8") as f:
    f.write("Archivo autogenerado\n")
    f.write(f"Generado: {datetime.now().isoformat()}\n")

print(f"Generado {OUT}")
