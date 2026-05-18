import java.util.Scanner; 

public class HolaMundo{
    public static void main (String[] args){ 
        Scanner teclado = new Scanner(System.in); 
        System.out.println("¿Cual es tu nombre? "); 
        String nombre = teclado.nextLine(); 
        System.out.println("Hola " + nombre + " ¿Como estas? "); 
    }
}