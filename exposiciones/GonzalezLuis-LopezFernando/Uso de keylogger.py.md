# Requisitos:
- Tener python instalado
- Tener instalado `pip`

# Pasos para ejecutar script
Ubicarse en el mismo nivel de directorio que el script de python `keylogger.py`

Ejecutar:
```bash
python -m venv venv_x11
```

```bash
source venv_x11/bin/activate
```

Y posteriormente instalar la biblioteca `pynput` con:
```bash
pip install pynput
```

Ahora si, se puede ejecutar el script, esperando que si tienes `x11`, keylogger registre todas las pulsaciones de tus teclas, mientras que si tienes `wayland`, no.
```bash
python keylogger.py
```

Recuerda que puedes saber el protocolo que tiene tu computadora con:
```bash
echo $XDG_SESSION_TYPE
```
