import sys
import argparse
from fuse import FUSE


def main():

    parser = argparse.ArgumentParser(description="FiUnamFS - Micro sistema de archivos multihilos")
    parser.add_argument("mount_point", help="Directorio vacío donde se montará FiUnamFS")
    parser.add_argument("image_file", help="Archivo de imagen del disco (ej. fiunamfs.img)")
    args = parser.parse_args()

    