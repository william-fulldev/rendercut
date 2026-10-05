import gestor_peliculas as gp
from pelicula import Pelicula
from recomendador import recomendar

import sqlite3
import pytest


def test_migracion_base_antigua(tmp_path):
    ruta = tmp_path / "vieja.db"
    c = sqlite3.connect(ruta)
    c.execute("CREATE TABLE peliculas(id INTEGER PRIMARY KEY AUTOINCREMENT, titulo TEXT NOT NULL, "
                "genero TEXT NOT NULL, duracion INTEGER NOT NULL, anyo_estreno INTEGER NOT NULL, "
                "director TEXT NOT NULL)")
    c.execute("INSERT INTO peliculas (titulo, genero, duracion, anyo_estreno, director) "
                "VALUES ('Alien','Terror',117,1979,'Ridley Scott')")
    c.commit()
    c.close()
    conn = gp.establecer_conexion(ruta)
    gp.crear_tablas(conn)
    gp.crear_tablas(conn)
    p = gp.listar_peliculas(conn)[0]
    assert p.titulo == "Alien" and p.estado == "pendiente" and p.valoracion is None
    conn.close()


def test_valorar_solo_vistas():
    with pytest.raises(ValueError):
        Pelicula(None, "A", "B", 90, 2000, "C", estado="pendiente", valoracion=4).validar()


def test_recomendador_respeta_tiempo_y_afinidad():
    pelis = [
        Pelicula(1, "Vista", "Ciencia ficción", 100, 2000, "X", "vista", 5, "2026-01-01"),
        Pelicula(2, "Larga", "Ciencia ficción", 200, 2000, "Y"),
        Pelicula(3, "Corta sci-fi", "Ciencia ficción", 110, 2001, "Z"),
        Pelicula(4, "Corta comedia", "Comedia", 110, 2001, "W"),
    ]
    titulos = [p.titulo for p, _ in recomendar(pelis, 120)]
    assert "Larga" not in titulos and "Vista" not in titulos
    assert titulos[0] == "Corta sci-fi"