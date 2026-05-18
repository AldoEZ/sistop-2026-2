public class Saludo {

    public static void main(String[] args) {
        if (args.length > 0){
            String nombre = args[0];
            System.out.println("Holaa " + nombre + "!!");
        }else{
            System.out.println("Hola Mundoo!!");
        }
        
    }
}