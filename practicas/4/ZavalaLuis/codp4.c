#include <stdio.h>
#include <unistd.h>

int main(){
	printf("Se está ejecutando proveniente del proceso con PID: %d\n", getpid());
	return 0;
}
