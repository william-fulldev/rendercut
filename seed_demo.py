"""Carga películas de ejemplo (algunas ya vistas, con nota y fecha) para la demo."""
from datetime import date, timedelta

import gestor_peliculas as gp
from pelicula import Pelicula

# (título, género, duración, año, director, estado, nota, días atrás en que se vio)
DEMO = [
    ("El padrino", "Drama", 175, 1972, "Francis Ford Coppola", "finalizada", 5, 130),
    ("Cadena perpetua", "Drama", 142, 1994, "Frank Darabont", "finalizada", 5, 100),
    ("Pulp Fiction", "Crimen", 154, 1994, "Quentin Tarantino", "pendiente", None, None),
    ("El caballero oscuro", "Acción", 152, 2008, "Christopher Nolan", "pendiente", None, None),
    ("Origen", "Ciencia ficción", 148, 2010, "Christopher Nolan", "finalizada", 4, 55),
    ("Interstellar", "Ciencia ficción", 169, 2014, "Christopher Nolan", "finalizada", 5, 20),
    ("Matrix", "Ciencia ficción", 136, 1999, "Lana y Lilly Wachowski", "finalizada", 4, 75),
    ("Alien, el octavo pasajero", "Terror", 117, 1979, "Ridley Scott", "finalizada", 4, 38),
    ("Blade Runner", "Ciencia ficción", 117, 1982, "Ridley Scott", "finalizada", 4, 12),
    ("Gladiator", "Acción", 155, 2000, "Ridley Scott", "pendiente", None, None),
    ("Seven", "Thriller", 127, 1995, "David Fincher", "finalizada", 4, 28),
    ("El silencio de los corderos", "Thriller", 118, 1991, "Jonathan Demme", "pendiente", None, None),
    ("Parásitos", "Thriller", 132, 2019, "Bong Joon-ho", "finalizada", 5, 5),
    ("El laberinto del fauno", "Fantasía", 118, 2006, "Guillermo del Toro", "pendiente", None, None),
    ("Mar adentro", "Drama", 125, 2004, "Alejandro Amenábar", "pendiente", None, None),
    ("El viaje de Chihiro", "Animación", 125, 2001, "Hayao Miyazaki", "pendiente", None, None),
    ("Akira", "Animación", 124, 1988, "Katsuhiro Otomo", "pendiente", None, None),
]


def cargar_demo(conn):
    """Inserta las películas que falten y actualiza las demo aún pendientes sin nota.

    Devuelve (añadidas, actualizadas).
    """
    hoy = date.today()
    existentes = {p.titulo: p for p in gp.listar_peliculas(conn)}
    añadidas = actualizadas = 0
    for titulo, genero, dur, anyo, director, estado, nota, dias in DEMO:
        fecha = (hoy - timedelta(days=dias)).isoformat() if dias is not None else None
        actual = existentes.get(titulo)
        if actual is None:
            gp.create_movie(conn, Pelicula(None, titulo, genero, dur, anyo, director, estado, nota, fecha))
            añadidas += 1
        elif estado == "finalizada" and actual.estado == "pendiente" and actual.valoracion is None:
            actual.estado, actual.valoracion, actual.fecha_visionado = estado, nota, fecha
            gp.actualizar_peli(conn, actual)
            actualizadas += 1
    return añadidas, actualizadas


if __name__ == "__main__":
    conn = gp.establecer_conexion()
    gp.crear_tablas(conn)
    a, u = cargar_demo(conn)
    print(f"✅ {a} películas añadidas, {u} actualizadas")
    gp.cerrar_conexion(conn)