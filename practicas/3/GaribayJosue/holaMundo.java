import java.util.Scanner;

public class holaMundo{
    public static void main(String[]args){
        Scanner teclado = new Scanner(System.in);
        System.out.println("Escribe tu nombre: ");
        String nombre = teclado.nextLine();

        System.out.println("Hola " + nombre + "!");

        teclado.close();
    }
}
