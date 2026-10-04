import gestor_peliculas as gp
from pelicula import Pelicula
import pytest


@pytest.fixture
def conn(tmp_path):
    c = gp.establecer_conexion(tmp_path / "test.db")
    gp.crear_tablas(c)
    yield c
    c.close()


def test_crear_y_consultar(conn):
    gp.create_movie(conn, Pelicula(None, "Alien", "Terror", 117, 1979, "Ridley Scott"))
    assert gp.consultar_peli(conn, "ali")[0][1] == "Alien"


def test_duracion_invalida(conn):
    with pytest.raises(ValueError):
        gp.create_movie(conn, Pelicula(None, "X", "Y", 0, 2000, "Z"))


def test_actualizar_id_inexistente(conn):
    assert gp.actualizar_peli(conn, Pelicula(999, "A", "B", 90, 2000, "C")) == 0