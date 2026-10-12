import gestor_peliculas as gp
from pelicula import Pelicula
from recomendador import recomendar

import sqlite3
# pyrefly: ignore [missing-import]
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

# TESTS DE LA FASE 4: géneros normalizados y títulos duplicados

# Esto es un "fixture": prepara una base de datos temporal y vacía para cada test
@pytest.fixture
def conexion(tmp_path):  # tmp_path es una carpeta temporal que da pytest y borra sola al acabar
    c = gp.establecer_conexion(tmp_path / "test_fase4.db")
    gp.crear_tablas(c)
    yield c  # Aquí le "presto" la conexión al test que la pida
    c.close()


def test_guardar_corrige_el_genero(conexion):  # Compruebo que el género mal escrito se arregla al guardar
    peli = Pelicula(None, "Matrix", "ciencia ficcion", 136, 1999, "Lana y Lilly Wachowski")
    gp.create_movie(conexion, peli)  # Guardo la película
    guardada = gp.listar_peliculas(conexion)[0]  # La leo de vuelta desde la base de datos
    assert guardada.genero == "Ciencia ficción"


def test_rechaza_titulo_duplicado(conexion):
    gp.create_movie(conexion, Pelicula(None, "Alien, el octavo pasajero", "Terror", 117, 1979, "Ridley Scott"))
    otra = Pelicula(None, "Alien: El octavo pasajero", "Terror", 117, 1979, "Ridley Scott")
    with pytest.raises(ValueError, match="Ya tienes"):  # Espero que salte el error con ese texto
        gp.create_movie(conexion, otra)  # Si esto no salta error, el test falla
    assert len(gp.listar_peliculas(conexion)) == 1  # la repetida no se tiene que haber guardado


def test_remake_con_otro_anyo_se_permite(conexion):  # Que no bloquee películas distintas con el mismo nombre
    gp.create_movie(conexion, Pelicula(None, "Dune", "Ciencia ficción", 155, 1984, "David Lynch"))  # La de 1984
    gp.create_movie(conexion, Pelicula(None, "Dune", "Ciencia ficción", 155, 2021, "Denis Villeneuve"))  # La de 2021: mismo título, otro año
    assert len(gp.listar_peliculas(conexion)) == 2  # Tienen que estar las dos guardadas


def test_editar_sin_cambios_no_es_duplicado(conexion):  # Que una peli no se compare consigo misma al editarla
    gp.create_movie(conexion, Pelicula(None, "Akira", "Animación", 124, 1988, "Katsuhiro Otomo"))
    peli = gp.listar_peliculas(conexion)[0]  # La recupero (ya con su id)
    peli.notas = "Me flipó la moto roja"  # Cambio solo las notas, el título y el año siguen igual
    assert gp.actualizar_peli(conexion, peli) == 1  # Tiene que actualizarse 1 fila, sin error de duplicado


def test_editar_hacia_un_duplicado_falla(conexion):  # Que no puedas pisar una película con el título de otra
    gp.create_movie(conexion, Pelicula(None, "Seven", "Thriller", 127, 1995, "David Fincher"))  # Primera película
    gp.create_movie(conexion, Pelicula(None, "Gladiator", "Acción", 155, 2000, "Ridley Scott"))  # Segunda película
    gladiator = [p for p in gp.listar_peliculas(conexion) if p.titulo == "Gladiator"][0]  # Busco la segunda por su título
    gladiator.titulo = "SEVEN"  # La renombro como la primera (en mayúsculas, que da igual)
    gladiator.anyo_estreno = 1995  # Y le pongo el mismo año
    with pytest.raises(ValueError, match="Ya tienes"):  # Ahora sí tiene que saltar el aviso de duplicado
        gp.actualizar_peli(conexion, gladiator)  # Si no salta, el test falla


def test_migracion_arregla_generos_viejos(conexion):  # Lo que hace crear_tablas con los géneros ya guardados
    conexion.execute(  # Meto dos películas a pelo con SQL, saltándome las validaciones, como si vinieran de antes
        "INSERT INTO peliculas (titulo, genero, duracion, anyo_estreno, director) VALUES (?,?,?,?,?)",
        ("Origen", "Ciencia Ficción", 148, 2010, "Christopher Nolan"),  # Con la F mayúscula, como la base real
    )
    conexion.execute(  # La segunda con otra variante fea del mismo género
        "INSERT INTO peliculas (titulo, genero, duracion, anyo_estreno, director) VALUES (?,?,?,?,?)",
        ("Interstellar", "ciencia ficcion", 169, 2014, "Christopher Nolan"),  # Todo en minúsculas y sin tilde
    )
    conexion.commit()  # Guardo esos dos inserts en la base
    gp.crear_tablas(conexion)  # Esto es lo que se ejecuta al abrir la app: aquí debería limpiarse
    gp.crear_tablas(conexion)  # Lo lanzo otra vez para comprobar que repetirlo no rompe nada
    generos = {p.genero for p in gp.listar_peliculas(conexion)}  # Saco los géneros distintos que quedaron (un set no repite)
    assert generos == {"Ciencia ficción"}  # Las dos tienen que haber acabado con el mismo género bueno
    