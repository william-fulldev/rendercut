import sqlite3
from pathlib import Path
from pelicula import Pelicula


# CONFIGURACIÓN

# Ruta absoluta anclada al directorio del proyecto: la db se localiza
# siempre aqui, sin importar desde que carpeta se ejecute el script.
DB_PATH = Path(__file__).resolve().parent / "bbdd_peliculas.db"

# Columnas añadidas en la Fase 3. Se usan para migrar bases de datos antiguas
# sin perder los datos que ya existen.
COLUMNAS_NUEVAS = {
    "estado": "TEXT NOT NULL DEFAULT 'pendiente'",
    "valoracion": "INTEGER",
    "fecha_visionado": "TEXT",
    "notas": "TEXT NOT NULL DEFAULT ''",
}

# Lista de columnas en el mismo orden que los campos de la clase Pelicula.
# Permite construir una Pelicula directamente con Pelicula(*fila).
_COLS = "id, titulo, genero, duracion, anyo_estreno, director, estado, valoracion, fecha_visionado, notas"


# CONEXIÓN Y ESTRUCTURA DE LA BASE DE DATOS

def establecer_conexion(db_path=DB_PATH):
    """Abre la conexión con SQLite. Acepta otra ruta (útil para los tests)."""
    return sqlite3.connect(db_path)


def cerrar_conexion(conn: sqlite3.Connection):
    """Cierra la conexión si existe."""
    if conn is not None:
        conn.close()


def crear_tablas(conn):
    """Crea la tabla si no existe, añade las columnas nuevas si faltan
    y normaliza estados antiguos.

    Es segura de ejecutar varias veces: no duplica ni borra nada.
    """
    with conn:
        # Estructura original de la tabla
        conn.execute('''CREATE TABLE IF NOT EXISTS peliculas(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            genero TEXT NOT NULL,
            duracion INTEGER NOT NULL,
            anyo_estreno INTEGER NOT NULL,
            director TEXT NOT NULL)''')

        # Migración: averiguamos qué columnas existen y añadimos las que faltan
        existentes = {fila[1] for fila in conn.execute("PRAGMA table_info(peliculas)")}
        for columna, definicion in COLUMNAS_NUEVAS.items():
            if columna not in existentes:
                conn.execute(f"ALTER TABLE peliculas ADD COLUMN {columna} {definicion}")

        # Normaliza estados antiguos o inválidos ('finalizada' pasa a 'vista')
        conn.execute("UPDATE peliculas SET estado = 'vista' WHERE estado = 'finalizada'")
        conn.execute(
            "UPDATE peliculas SET estado = 'pendiente' "
            "WHERE estado NOT IN ('pendiente', 'viendo', 'vista')"
        )

# ESCRITURA: CREAR, ACTUALIZAR Y ELIMINAR

def _valores(p: Pelicula):
    """Convierte una Pelicula en la tupla de 9 valores que esperan INSERT y UPDATE.

    El orden debe coincidir con las columnas de las consultas SQL.
    """
    return (
        p.titulo.strip(),
        p.genero.strip(),
        p.duracion,
        p.anyo_estreno,
        p.director.strip(),
        p.estado,
        p.valoracion,
        p.fecha_visionado or None,   # Si no hay fecha, se guarda NULL
        (p.notas or "").strip(),
    )


def create_movie(conn, pelicula: Pelicula):
    """Valida e inserta una película nueva."""
    pelicula.validar()
    with conn:
        conn.execute(
            '''INSERT INTO peliculas (titulo, genero, duracion, anyo_estreno, director,
            estado, valoracion, fecha_visionado, notas) VALUES (?,?,?,?,?,?,?,?,?)''',
            _valores(pelicula),
        )


def actualizar_peli(conn: sqlite3.Connection, pelicula: Pelicula) -> int:
    """Valida y actualiza una película. Devuelve cuántas filas cambió (0 = ID inexistente)."""
    pelicula.validar()
    with conn:
        cur = conn.execute(
            '''UPDATE peliculas SET titulo=?, genero=?, duracion=?, anyo_estreno=?, director=?,
            estado=?, valoracion=?, fecha_visionado=?, notas=? WHERE id=?''',
            _valores(pelicula) + (pelicula.id,),
        )
        return cur.rowcount


def eliminar_pelicula(conn: sqlite3.Connection, titulo: str = None, id_peli: int = None) -> int:
    """Elimina por ID o por título. Devuelve cuántas filas borró."""
    with conn:
        cursor = conn.cursor()
        if id_peli is not None:
            cursor.execute("DELETE FROM peliculas WHERE id = ?", (id_peli,))
        elif titulo is not None:
            cursor.execute("DELETE FROM peliculas WHERE LOWER(titulo) = ?", (titulo.strip().lower(),))
        else:
            return 0
        return cursor.rowcount


# LECTURA

def consultar_peli(conn: sqlite3.Connection, titulo: str) -> list:
    """Busca por título (contiene el texto). Devuelve tuplas de 6 columnas.

    Se mantiene tal cual porque la interfaz actual usa índices (p[0], p[1]...).
    """
    sql = "SELECT id, titulo, genero, duracion, anyo_estreno, director FROM peliculas WHERE LOWER(titulo) LIKE ?"
    cursor = conn.cursor()
    cursor.execute(sql, (f"%{titulo.lower()}%",))
    resultados = cursor.fetchall()
    cursor.close()
    return resultados


def consultar_peli_por_id(conn: sqlite3.Connection, id_peli: int):
    """Devuelve una tupla de 6 columnas con la película de ese ID, o None."""
    sql = "SELECT id, titulo, genero, duracion, anyo_estreno, director FROM peliculas WHERE id = ?"
    cursor = conn.cursor()
    cursor.execute(sql, (id_peli,))
    resultado = cursor.fetchone()
    cursor.close()
    return resultado


def listar_peliculas(conn, titulo: str = "") -> list[Pelicula]:
    """Devuelve objetos Pelicula completos (con estado, valoración, fecha y notas)."""
    filas = conn.execute(
        f"SELECT {_COLS} FROM peliculas WHERE LOWER(titulo) LIKE ? ORDER BY titulo COLLATE NOCASE",
        (f"%{titulo.lower()}%",),
    ).fetchall()
    return [Pelicula(*f) for f in filas]


def obtener_pelicula(conn, id_peli: int) -> Pelicula | None:
    """Devuelve una Pelicula completa por ID, o None si no existe."""
    fila = conn.execute(f"SELECT {_COLS} FROM peliculas WHERE id = ?", (id_peli,)).fetchone()
    return Pelicula(*fila) if fila else None


# MODO CONSOLA (CLI)

def pedir_entero(mensaje: str) -> int:
    """Pide un número entero y repite la pregunta hasta que sea válido."""
    while True:
        try:
            return int(input(mensaje))
        except ValueError:
            print("⚠️ Introduce un número entero.")


def pedir_pelicula(id_peli=None) -> Pelicula:
    """Pide los datos de una película y los valida. Repite si hay errores."""
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
    """Bucle del menú de consola: añadir, eliminar, consultar y actualizar."""
    while True:
        option = input("\n¿Quieres añadir(1), eliminar(2), consultar(3) o actualizar(4) una película? (otra tecla = salir): ")

        # Añadir
        if option == "1":
            pelicula = pedir_pelicula()
            create_movie(conn, pelicula)
            print(f"\n✅ Película '{pelicula.titulo}' insertada correctamente")

        # Eliminar por ID o por título
        elif option == "2":
            criterio = input("\n¿Eliminar por ID (1) o por título (2)?: ")
            if criterio == "1":
                filas = eliminar_pelicula(conn, id_peli=pedir_entero("ID de la película: "))
            else:
                filas = eliminar_pelicula(conn, titulo=input("Título de la película: "))
            print("\n🗑️ Película eliminada correctamente" if filas > 0 else "\n⚠️ No se encontró ninguna película para eliminar")

        # Consultar e imprimir resultados
        elif option == "3":
            titulo = input("\nTítulo a consultar: ")
            resultados = consultar_peli(conn, titulo)
            if resultados:
                for r in resultados:
                    print(f"[{r[0]}] {r[1]} ({r[4]}) - {r[2]}, {r[3]} min, dir. {r[5]}")
            else:
                print("\n⚠️ No se encontraron películas.")

        # Actualizar
        elif option == "4":
            pelicula = pedir_pelicula(pedir_entero("\nID de la película a actualizar: "))
            if actualizar_peli(conn, pelicula) > 0:
                print(f"\n✅ Película '{pelicula.titulo}' actualizada correctamente")
            else:
                print("\n⚠️ No existe ninguna película con ese ID")

        # Cualquier otra tecla: salir
        else:
            print("\nFin del programa. Adiós.")
            break
