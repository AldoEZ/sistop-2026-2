import os

def main():
    print(f"Se está ejecutando proveniente del proceso con PID: {os.getpid()}")

if __name__ == "__main__":
    main()