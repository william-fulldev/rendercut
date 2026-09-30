import sqlite3
from pathlib import Path
from pelicula import Pelicula

#conn=None

# Ruta absoluta anclada al directorio del proyecto: la db se localiza
# siempre aqui, sin importar desde que carpeta se ejecute el script.
DB_PATH = Path(__file__).resolve().parent / "bbdd_peliculas.db"


def establecer_conexion():
    conn = sqlite3.connect(DB_PATH)
    return conn

def crear_tablas(conn):

    sql ='''CREATE TABLE IF NOT EXISTS peliculas(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        genero TEXT NOT NULL,
        duracion INTEGER NOT NULL,
        anyo_estreno INTEGER NOT NULL,
        director TEXT NOT NULL)'''
    cursor =conn.cursor()
    cursor.execute(sql)
    conn.commit()


def create_movie(conn, pelicula:Pelicula):
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO peliculas 
    (titulo, genero, duracion, anyo_estreno, director) VALUES (?,?,?,?,?)''',
    (pelicula.titulo, pelicula.genero, pelicula.duracion,
pelicula.anyo_estreno, pelicula.director))
    conn.commit()
    cursor.close()

def cerrar_conexion(conn: sqlite3.Connection):
    if conn != None:
        conn.close()

def eliminar_pelicula(conn: sqlite3.Connection, titulo: str = None, id_peli: int = None) -> int:
    with conn:
        cursor = conn.cursor()
        if id_peli is not None:
            sql = "DELETE FROM peliculas WHERE id = ?"
            cursor.execute(sql, (id_peli,))
        elif titulo is not None:
            sql = "DELETE FROM peliculas WHERE LOWER(titulo) = ?"
            cursor.execute(sql, (titulo.strip().lower(),))
        else:
            return 0
        return cursor.rowcount


def consultar_peli(conn: sqlite3.Connection, titulo: str) -> list:
    sql = "SELECT id, titulo, genero, duracion, anyo_estreno, director FROM peliculas WHERE LOWER(titulo) LIKE ?"
    cursor = conn.cursor()
    cursor.execute(sql, (f"%{titulo.lower()}%",))
    resultados = cursor.fetchall()
    cursor.close()
    return resultados 

def consultar_peli_por_id(conn: sqlite3.Connection, id_peli: int):
    sql = "SELECT id, titulo, genero, duracion, anyo_estreno, director FROM peliculas WHERE id = ?"
    cursor = conn.cursor()
    cursor.execute(sql, (id_peli,))
    resultado = cursor.fetchone()
    cursor.close()
    return resultado 

def actualizar_peli(conn:sqlite3.Connection, pelicula:Pelicula):
    if (conn == None):
        conn=establecer_conexion()
    cursor = conn.cursor()
    cursor.execute('''UPDATE peliculas SET titulo = ?, genero = ?, duracion = ?, anyo_estreno = ?, director = ? WHERE id = ?''',
    (pelicula.titulo, pelicula.genero, pelicula.duracion,
pelicula.anyo_estreno, pelicula.director, pelicula.id))
    conn.commit()

def menu_principal(conn: sqlite3.Connection):
    while True:
        option=input("\n¿Quieres añadir(1), eliminar(2), consultar(3) o actualizar(4) una pelicula?: \n")
        if option=="1":
            titulo=input("\nIntroduce el titulo de la pelicula: ")
            genero=input("\nIntroduce el genero de la pelicula: ")
            duracion=int(input("\nIntroduce la duracion de la pelicula: "))
            anyo=int(input("\nIntroduce el año de la pelicula: "))
            director=input("\nIntroduce el director de la pelicula: ")
            pelicula=Pelicula(None, titulo, genero, duracion, anyo, director)
            create_movie(conn, pelicula)
            print(f"\n✅ Pelicula '{titulo}' insertada correctamente")
        elif option == "2":
            criterio = input("\n¿Quieres eliminar por ID (1) o por Título (2)?: ")
            if criterio == "1":
                id_eliminar = int(input("Introduce el ID de la película: "))
                filas = eliminar_pelicula(conn, id_peli=id_eliminar)
            else:
                titulo_eliminar = input("Introduce el título de la película: ")
                filas = eliminar_pelicula(conn, titulo=titulo_eliminar)

            if filas > 0:
                print(f"\n🗑️ Película eliminada correctamente")
            else:
                print("\n⚠️ No se encontró ninguna película para eliminar")

        elif option=="3":
            titulo=input("\nIntroduce el titulo de la pelicula que quieres consultar: ")
            consultar_peli(conn, titulo)
            print(f"\n🔍 Pelicula '{titulo}' consultada correctamente")
        elif option=="4":
            id_peli=int(input("\nIntroduce el id de la pelicula que quieres actualizar: "))
            titulo=input("\nIntroduce el titulo de la pelicula: ")
            genero=input("\nIntroduce el genero de la pelicula: ")
            duracion=int(input("\nIntroduce la duracion de la pelicula: "))
            anyo=int(input("\nIntroduce el año de la pelicula: "))
            director=input("\nIntroduce el director de la pelicula: ")
            pelicula=Pelicula(id_peli, titulo, genero, duracion, anyo, director)
            actualizar_peli(conn, pelicula)
            print(f"\n✅ Pelicula '{titulo}' actualizada correctamente")
        else:
            print("\nFin del programa. Adios.")
            break
