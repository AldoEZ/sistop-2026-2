from pathlib import Path

ruta = Path("fiunamfs.img")

datos = bytearray(ruta.read_bytes())

# nueva version, para que vaya a corde con lo establecido
datos[14:18] = b"26-2"

ruta.write_bytes(datos)