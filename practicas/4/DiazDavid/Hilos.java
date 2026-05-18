public class Hilos { 
	
	public static void main(String[] args) {
		System.out.println("Iniciando el hilo principal...");
		
		Thread  hilo_1 = new Thread(() -> {
			for (int i = 1; i <= 5; i++) {
				System.out.println("Hilo 1 - Iteracion: " + i);
				try {
					Thread.sleep(500);
				} catch (InterruptedException e) {
					System.out.println("El Hilo 1 ha sido interrumpido");
				}
			}
		});
		
		Thread hilo_2 = new Thread(() -> {
			for (int i = 1; i <= 5; i++) {
				System.out.println("Hilo 2 - Iteracion: " + i);
				try {
					Thread.sleep(500);
				} catch (InterruptedException e) {
					System.out.println("El Hilo 2 ha sido interrumpido");
				}
			}
		});
		
		hilo_1.start();
		hilo_2.start();

		System.out.println("El hilo principal ha terminado");
	}
}
