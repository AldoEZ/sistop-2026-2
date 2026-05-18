#!/usr/bin/python3
#
# Este programita ejemplo es para ilustrar la llamada execve() desde
# llama_con_exec.py
import os
import time
import yaml
import sys

pid = os.getpid()
print(f"¡Hola! Este es un programita muy sencillo. Su PID es {pid}")
print('Mi lista de argumentos:')
print(yaml.dump(sys.argv))
# print('Mi terminal:')
# print(yaml.dump(os.environ['TERM']))

