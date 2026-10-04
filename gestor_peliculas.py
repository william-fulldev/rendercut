import sqlite3
from pathlib import Path
from pelicula import Pelicula

#conn=None

# Ruta absoluta anclada al directorio del proyecto: la db se localiza
# siempre aqui, sin importar desde que carpeta se ejecute el script.
DB_PATH = Path(__file__).resolve().parent / "bbdd_peliculas.db"


def establecer_conexion(db_path=DB_PATH):
    return sqlite3.connect(db_path)

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

# Validacion y creacion de una pelicula
def create_movie(conn, pelicula: Pelicula):
    pelicula.validar()
    with conn:
        conn.execute(
            "INSERT INTO peliculas (titulo, genero, duracion, anyo_estreno, director) VALUES (?,?,?,?,?)",
            (pelicula.titulo.strip(), pelicula.genero.strip(), pelicula.duracion,
            pelicula.anyo_estreno, pelicula.director.strip()),
        )

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

# Validacion y actualizacion de una pelicula
def actualizar_peli(conn: sqlite3.Connection, pelicula: Pelicula) -> int:
    pelicula.validar()
    with conn:
        cur = conn.execute(
            "UPDATE peliculas SET titulo=?, genero=?, duracion=?, anyo_estreno=?, director=? WHERE id=?",
            (pelicula.titulo.strip(), pelicula.genero.strip(), pelicula.duracion,
            pelicula.anyo_estreno, pelicula.director.strip(), pelicula.id),
        )
        return cur.rowcount

# Pedir un entero de forma segura
def pedir_entero(mensaje: str) -> int:
    while True:
        try:
            return int(input(mensaje))
        except ValueError:
            print("⚠️ Introduce un número entero.")


def pedir_pelicula(id_peli=None) -> Pelicula:
    while True:
        pelicula = Pelicula(
            id_peli,
            input("\nTítulo: "),
            input("Género: "),
            pedir_entero("Duración (min): "),
            pedir_entero("Año de estreno: "),
            input("Director: "),
        )
        try:
            pelicula.validar()
            return pelicula
        except ValueError as ex:
            print(f"⚠️ {ex} Inténtalo de nuevo.")


def menu_principal(conn: sqlite3.Connection):
    while True:
        option = input("\n¿Quieres añadir(1), eliminar(2), consultar(3) o actualizar(4) una película? (otra tecla = salir): ")
        if option == "1":
            pelicula = pedir_pelicula()
            create_movie(conn, pelicula)
            print(f"\n✅ Película '{pelicula.titulo}' insertada correctamente")
        elif option == "2":
            criterio = input("\n¿Eliminar por ID (1) o por título (2)?: ")
            if criterio == "1":
                filas = eliminar_pelicula(conn, id_peli=pedir_entero("ID de la película: "))
            else:
                filas = eliminar_pelicula(conn, titulo=input("Título de la película: "))
            print("\n🗑️ Película eliminada correctamente" if filas > 0
                else "\n⚠️ No se encontró ninguna película para eliminar")
        elif option == "3":
            titulo = input("\nTítulo a consultar: ")
            resultados = consultar_peli(conn, titulo)
            if resultados:
                for r in resultados:
                    print(f"[{r[0]}] {r[1]} ({r[4]}) - {r[2]}, {r[3]} min, dir. {r[5]}")
            else:
                print("\n⚠️ No se encontraron películas.")
        elif option == "4":
            pelicula = pedir_pelicula(pedir_entero("\nID de la película a actualizar: "))
            if actualizar_peli(conn, pelicula) > 0:
                print(f"\n✅ Película '{pelicula.titulo}' actualizada correctamente")
            else:
                print("\n⚠️ No existe ninguna película con ese ID")
        else:
            print("\nFin del programa. Adiós.")
            break