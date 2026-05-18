//Autores: Navarro Carbajal Fredy Emiliano, Ramirez Teran Emily
#include <iostream>
#include <vector>
#include <map>
#include <thread>
#include <mutex>
#include <chrono>
#include <random>
#include <ncurses.h>
using namespace std;

//Las cuatro dirreciones posibles en la interseccion 
enum class Direccion{
    NORTE, ESTE, SUR, OESTE
};

//Conversion de las coordenadas para su uso en el panel de estados
string dir_a_string(Direccion x){
    if(x == Direccion::NORTE) return "N";
    if(x == Direccion::ESTE)  return "E";
    if(x == Direccion::SUR)   return "S";
    if(x == Direccion::OESTE) return "O";
    return "*";
}

//Estructura auto (hilo) para visualizar sus movimientos
struct EstadoAuto{
    int x, y;
    Direccion origen;
    Direccion destino;
    vector<int> ruta;
};

map<int, EstadoAuto> posiciones_vivas; //Mapeo que ayuda a la parte visual, para saber donde dibujar
typedef pair<Direccion, Direccion> Ruta; //Fomato para las rutas
mutex m_posiciones; //Mutex para proteger el acceso

//Mapeo de las rutas posibles (desde los 4 puntos existentes), y las 3 combinaciones de movimientos
map<Ruta, vector<int>> tabla_rutas = {
    //El mapa se define a partir de una ruta y los cuadrantes que ocupara que ruta dependiendo su origen
    //Inicio = SUR
    {{Direccion::SUR, Direccion::ESTE},  {3}},       //Fin: vuelta a la derecha 
    {{Direccion::SUR, Direccion::NORTE}, {3, 0}},    //Fin: seguir derecho
    {{Direccion::SUR, Direccion::OESTE}, {3, 0, 1}}, //Fin: vuelta a la izquierda

    //Inicio = NORTE
    {{Direccion::NORTE, Direccion::OESTE}, {1}},       //Fin: vuelta a la derecha
    {{Direccion::NORTE, Direccion::SUR},   {1, 2}},    //Fin: seguir derecho 
    {{Direccion::NORTE, Direccion::ESTE},  {1, 2, 3}}, //Fin: vuelta a la izquierda

    //Inicio = ESTE
    {{Direccion::ESTE, Direccion::NORTE}, {0}},       //Fin: vuelta a la derecha
    {{Direccion::ESTE, Direccion::OESTE}, {0, 1}},    //Fin: seguir derecho 
    {{Direccion::ESTE, Direccion::SUR},   {0, 1, 2}}, //Fin: vuelta a la izquierda

    //Inicio = OESTE
    {{Direccion::OESTE, Direccion::SUR},   {2}},       //Fin: vuelta a la derecha
    {{Direccion::OESTE, Direccion::ESTE},  {2, 3}},    //Fin: seguir derecho 
    {{Direccion::OESTE, Direccion::NORTE}, {2, 3, 0}}  //Fin: vuelta a la izquierda
};

//Control para el paso de los autos
class ControlPaso{
private:
    mutex m_cuadrantes[4]; //Los 4 recursos indican los cutro cuadrantes que podemos usar en la interseccion [Q0,Q1,Q2,Q3]
public:
    void solicitar_paso(int id, const vector<int>& ruta){
            
        //Bloqueo para evitar deadlock
        if(ruta.size() == 1){
            m_cuadrantes[ruta[0]].lock(); //Bloqueo de un solo cuadrante que necesita
        }else if(ruta.size() == 2){
            lock(m_cuadrantes[ruta[0]], m_cuadrantes[ruta[1]]); //En caso de que la ruta requiera 2 o 3 cuadrantes, se bloquean todos 
        }else if(ruta.size() == 3){                             //ya que puede generar un deadlock, ya que si no hay una regla clara, los autos no sabrian quien pasar y quien no                 
            lock(m_cuadrantes[ruta[0]], m_cuadrantes[ruta[1]], m_cuadrantes[ruta[2]]);
        }
    }

    //Libera los cuadrantes (recursos) simpre y cuando el auto salga
    void liberar_paso(int id, const vector<int>& ruta){
        for(int x : ruta){
            m_cuadrantes[x].unlock();
        }
    }
};

//Actualiza las nuevas coordenadas
void actualizar_posicion(int id, int q_actual){
    lock_guard<mutex> lock(m_posiciones);
    if(q_actual == 0){ posiciones_vivas[id].y = 11; posiciones_vivas[id].x = 34;}         //Norte-Este
    else if(q_actual == 1){ posiciones_vivas[id].y = 11; posiciones_vivas[id].x = 31;}    //Norte-Oeste
    else if(q_actual == 2){ posiciones_vivas[id].y = 14; posiciones_vivas[id].x = 31;}    //Sur-Oeste
    else if(q_actual == 3){ posiciones_vivas[id].y = 14; posiciones_vivas[id].x = 34;}    //Sur-Este
}

//Establece las coordenadas de la entrada del auto 
void set_posicion(int id, Direccion origen){
    lock_guard<mutex> lock(m_posiciones);
    if(origen == Direccion::NORTE){ posiciones_vivas[id].x = 31; posiciones_vivas[id].y = 5;}
    else if(origen == Direccion::SUR){ posiciones_vivas[id].x = 34; posiciones_vivas[id].y = 20;}
    else if(origen == Direccion::ESTE){ posiciones_vivas[id].x = 50; posiciones_vivas[id].y = 11;} 
    else if(origen == Direccion::OESTE){ posiciones_vivas[id].x = 10; posiciones_vivas[id].y = 14;} 
}

//Establece la salida del auto
void set_posicion_salida(int id, Direccion destino){
    lock_guard<mutex> lock(m_posiciones);
    if(destino == Direccion::NORTE){ posiciones_vivas[id].x = 34; posiciones_vivas[id].y = 5;}  
    else if(destino == Direccion::SUR){ posiciones_vivas[id].x = 31; posiciones_vivas[id].y = 20;} 
    else if(destino == Direccion::ESTE){ posiciones_vivas[id].x = 50; posiciones_vivas[id].y = 14;} 
    else if(destino == Direccion::OESTE){ posiciones_vivas[id].x = 10; posiciones_vivas[id].y = 11;} 
}

//Establece la posicion dentro de la interseccion
void set_posicion_cuadrante(int id, int q_actual){
    lock_guard<mutex> lock(m_posiciones);
    if(q_actual == 0){ posiciones_vivas[id].y = 11; posiciones_vivas[id].x = 34;}
    else if(q_actual == 1){ posiciones_vivas[id].y = 11; posiciones_vivas[id].x = 31;} 
    else if(q_actual == 2){ posiciones_vivas[id].y = 14; posiciones_vivas[id].x = 31;} 
    else if(q_actual == 3){ posiciones_vivas[id].y = 14; posiciones_vivas[id].x = 34;} 
}

void hilo_visual(){
    initscr(); //Toma el control de la terminal ncurses
    curs_set(0); //Oculta el cursor
    start_color(); 
    init_pair(1, COLOR_CYAN, COLOR_BLACK); //Estable el color para los autos
    init_pair(2, COLOR_WHITE, COLOR_BLACK); //Establece el color para las calles y cuadrantes

    while(true){
        erase(); //Elimina todo lo que se dibujo antes, para dar paso a lo nuevo 
        attron(COLOR_PAIR(2)); //Color
        mvaddstr(1, 10, "--- INTERSECCION DE CAMINOS - SIMULACION ---"); //Imprime el titulo en las coordenadas dasdas

        //Dibuja las calles verticales
        for(int i = 4; i < 10; i++)  mvaddstr(i, 30, "|  |  |"); 
        for(int i = 16; i < 22; i++) mvaddstr(i, 30, "|  |  |");
        //Dibuja coordenadas horizontales de las calles
        mvaddstr(10, 5, "-----------------      -----------------");
        mvaddstr(12, 5, "      ---              ---      "); 
        mvaddstr(13, 30, "  |  "); 
        mvaddstr(15, 5, "-----------------      -----------------");

    
        attron(A_DIM); //Color (brillo bajo) de cuadrantes
        mvaddstr(11, 31, "Q1"); //Imprime los cuadrantes [Q0, Q1, Q2, Q3]
        mvaddstr(11, 34, "Q0");
        mvaddstr(14, 31, "Q2"); 
        mvaddstr(14, 34, "Q3");
        attroff(A_DIM);
        attroff(COLOR_PAIR(2));

        //Dibujamos el panel de los estados de los coches
        int fila_panel = 4;
        int columna_panel = 50; 

        attron(A_BOLD | COLOR_PAIR(1));
        mvaddstr(fila_panel++, columna_panel, "ID  | RUTA      | CUADRANTES");
        attroff(A_BOLD | COLOR_PAIR(1));
        mvaddstr(fila_panel++, columna_panel, "----------------------------");

        {
            lock_guard<mutex> lock(m_posiciones);
            //Dibujamos la lista de autos activos en el panel de estados
            for(auto const& [id, datos] : posiciones_vivas){
                string qs = "";
                for(int q : datos.ruta) qs += "Q" + to_string(q) + " ";

                //Imprimimos la informacion del auto en el panel
                mvprintw(fila_panel++, columna_panel, "A%d  | %s -> %s | %s", 
                         id, 
                         dir_a_string(datos.origen).c_str(), 
                         dir_a_string(datos.destino).c_str(),
                         qs.c_str());

                //Imprimimos el auto en el mapa
                attron(COLOR_PAIR(1) | A_BOLD);
                mvprintw(datos.y, datos.x, "A%d", id);
                attroff(COLOR_PAIR(1) | A_BOLD);
            }
        }

        refresh();
        this_thread::sleep_for(chrono::milliseconds(100)); 
    }
    endwin();
}

void hilo_auto(int id, Direccion origen, Direccion destino, ControlPaso& gestor){
    vector<int> mi_ruta = tabla_rutas[make_pair(origen, destino)];

    //Registro inicial de auto para su visualizacion
    {
        lock_guard<mutex> lock(m_posiciones);
        posiciones_vivas[id] = {0, 0, origen, destino, mi_ruta}; 
    }

    //Establece de donde se origina el coche
    set_posicion(id, origen);
    this_thread::sleep_for(chrono::milliseconds(1000 + rand() % 500)); 

    //El auto (hilo) solitica si puede pasar, siempre y cuando este disponible los recursos
    gestor.solicitar_paso(id, mi_ruta);

    //El auto cruza la interseccion ya que tiene los recuros
    for(int cuadrante : mi_ruta){
        set_posicion_cuadrante(id, cuadrante);
        this_thread::sleep_for(chrono::milliseconds(1500)); 
    }

    //Libera los recursos y establece la posicion del auto
    gestor.liberar_paso(id, mi_ruta);
    set_posicion_salida(id, destino);
    this_thread::sleep_for(chrono::milliseconds(1000)); 

    //Limpia la memoria para la parte visual
    {
        lock_guard<mutex> lock(m_posiciones);
        posiciones_vivas.erase(id);
    }
}

int main(){
    ControlPaso gestor; //Creacion del objeto para los 4 muxes
    vector<thread> autos; //Creacion de la lista de autos (hilos)
    vector<Direccion> dir = {Direccion::NORTE, Direccion::ESTE, Direccion::SUR, Direccion::OESTE}; //Direcciones que podemos elegir

    thread visualizador(hilo_visual); //Creacion del hilo para visuizarlo (interfaz usuario)
    visualizador.detach(); 

    this_thread::sleep_for(chrono::milliseconds(200));

    //Genera hilos (autos)
    for(int i = 0; i < 8; i++){
        Direccion entrada = dir[rand() % 4]; //Generamos entrada random
        Direccion salida = dir[rand() % 4]; //Generamos salida random
        while(entrada == salida) salida = dir[rand() % 4]; //Para evitar que salida y entrada, sean las mismas

        autos.emplace_back(hilo_auto, i, entrada, salida, ref(gestor)); //Genera un nuevo auto (hilo)
        this_thread::sleep_for(chrono::milliseconds(2500)); 
    }

    for(auto& t : autos) t.join(); //Espera para que todos los autos (hilos) finalicen

    this_thread::sleep_for(chrono::seconds(1));
    return 0;
}
