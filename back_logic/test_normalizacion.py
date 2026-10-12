from normalizacion import normalizar_genero, buscar_duplicado
from pelicula import Pelicula


def test_genero_mayusculas_y_tildes():  # Prueba que distintas formas den el mismo resultado
    for escrito in ("Ciencia Ficción", "ciencia ficcion", "  CIENCIA   FICCIÓN ", "Sci-Fi"):  # Cuatro variantes
        assert normalizar_genero(escrito) == "Ciencia ficción"  # Todas deben quedar igual


def test_genero_desconocido():  # Un género que no está en la lista
    assert normalizar_genero("documental") == "Documental"  # Solo se corrige la mayúscula inicial


def test_duplicado_por_puntuacion():  # El caso real de tu captura de Biblioteca
    guardadas = [Pelicula(1, "Alien, el octavo pasajero", "Terror", 117, 1979, "Ridley Scott")]  # Ya existe
    assert buscar_duplicado(guardadas, "Alien: El octavo pasajero", 1979) is not None  # Debe detectarse


def test_mismo_titulo_otro_anyo_no_es_duplicado():  # Los remakes no deben bloquearse
    guardadas = [Pelicula(1, "Dune", "Ciencia ficción", 155, 1984, "David Lynch")]  # Versión de 1984
    assert buscar_duplicado(guardadas, "Dune", 2021) is None  # La de 2021 es otra película


def test_al_editar_no_se_compara_consigo_misma():  # Evita un falso positivo al guardar cambios
    guardadas = [Pelicula(7, "Akira", "Animación", 124, 1988, "Katsuhiro Otomo")]  # Película con id 7
    assert buscar_duplicado(guardadas, "Akira", 1988, id_ignorar=7) is None  # Ignoramos su propio id