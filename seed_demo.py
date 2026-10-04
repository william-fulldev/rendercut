"""Carga películas de ejemplo para probar el gestor."""
import gestor_peliculas as gp
from pelicula import Pelicula

DEMO = [
    ("El padrino", "Drama", 175, 1972, "Francis Ford Coppola"),
    ("Cadena perpetua", "Drama", 142, 1994, "Frank Darabont"),
    ("Pulp Fiction", "Crimen", 154, 1994, "Quentin Tarantino"),
    ("El caballero oscuro", "Acción", 152, 2008, "Christopher Nolan"),
    ("Origen", "Ciencia ficción", 148, 2010, "Christopher Nolan"),
    ("Interstellar", "Ciencia ficción", 169, 2014, "Christopher Nolan"),
    ("Matrix", "Ciencia ficción", 136, 1999, "Lana y Lilly Wachowski"),
    ("Alien, el octavo pasajero", "Terror", 117, 1979, "Ridley Scott"),
    ("Blade Runner", "Ciencia ficción", 117, 1982, "Ridley Scott"),
    ("Gladiator", "Acción", 155, 2000, "Ridley Scott"),
    ("Seven", "Thriller", 127, 1995, "David Fincher"),
    ("El silencio de los corderos", "Thriller", 118, 1991, "Jonathan Demme"),
    ("Parásitos", "Thriller", 132, 2019, "Bong Joon-ho"),
    ("El laberinto del fauno", "Fantasía", 118, 2006, "Guillermo del Toro"),
    ("Mar adentro", "Drama", 125, 2004, "Alejandro Amenábar"),
    ("El viaje de Chihiro", "Animación", 125, 2001, "Hayao Miyazaki"),
    ("Akira", "Animación", 124, 1988, "Katsuhiro Otomo"),
]


def cargar_demo(conn) -> int:
    añadidas = 0
    for titulo, genero, duracion, anyo, director in DEMO:
        if not gp.consultar_peli(conn, titulo):
            gp.create_movie(conn, Pelicula(None, titulo, genero, duracion, anyo, director))
            añadidas += 1
    return añadidas


if __name__ == "__main__":
    conn = gp.establecer_conexion()
    gp.crear_tablas(conn)
    print(f"✅ {cargar_demo(conn)} películas añadidas")
    gp.cerrar_conexion(conn)
    