#!/usr/bin/python3
import os
import yaml

pid = os.getpid()
print("Este es otro programita muy sencillo, pero con...")
print(f"Algo más. ¡Ah! Mi PID es {pid}.")
# print('Mi terminal:')
# print(yaml.dump(os.environ['TERM']))

os.execve("programita_sencillo.py", ['¡Cuac!', '-v', '/dev/null'], {})
