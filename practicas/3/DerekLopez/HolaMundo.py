import sys

def main():
    if len(sys.argv)>1:
        print(f"Hola, {sys.argv[1]}")
    else:
        print("Hola,usuario")

if __name__ == "__main__":
    main()
