extern "C" {
    fn fork() -> i32;
    fn getpid() -> i32;
    fn getppid() -> i32;
}

fn main() {
    unsafe {
        let pid = fork();

        if pid < 0{
            eprintln!("Error al creal el fork");
            return;
        }

        if pid > 0{
            std::process::exit(0);
        }

        println!("Mi PID es {}, el de mi padre es {}", getpid(), getppid());

        loop{}

    }

}

