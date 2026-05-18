#include <stdio.h>
#include <omp.h>

int main() {
	#pragma omp parallel
    {
        int i;
        for(i=0;i<4;i++){
            printf("Hilo número %d, Iteracion: %d\n", omp_get_thread_num(),i);
        }
	}
	printf("Adios \n");
	return 0;
} 