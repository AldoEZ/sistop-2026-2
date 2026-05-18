use std::io;

fn main(){
    println!("no tengo la creatividad para escribir algo distinto a 'hola mundo'");
    println!("se te ocurre algo?");

    let mut name = String::new();

    io::stdin()
        .read_line(&mut name);

    println!("Que buena idea!!: {}", name);
}
