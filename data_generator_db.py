"""Generador de datos de empleados para SQLite.

Este módulo crea una base de datos SQLite con una tabla de empleados
y rellena registros aleatorios según parámetros de usuario. Incluye
clases, utilidades de conexión e inserción masiva.
"""

import time
import random
import sqlite3
from dataclasses import dataclass
from pathlib import Path

NUMERO_REGISTROS_DEFAULT = 100
NOMBRE_DATABASE = 'db_empleados_optimizado.sqlite3'
SALARIO_MINIMO_DEFAULT = 18_000
SALARIO_MAXIMO_DEFAULT = 50_000

# Ruta base del proyecto: siempre la carpeta donde vive este script.
# Así evitamos que SQLite cree bases de datos fantasma al ejecutar
# el generador desde otro directorio de trabajo.
BASE_DIR = Path(__file__).resolve().parent

@dataclass
class Empleado:
    nombre : str
    apellidos : str
    categoria_profesional : str
    ciudad : str
    salario : int
    id: int = None

# Lista de 20 nombres (masculinos y femeninos)
nombres = [
    "Carlos", "María", "Juan", "Lucía", "Pedro",
    "Ana", "Luis", "Elena", "Jorge", "Carmen",
    "Diego", "Sofía", "Miguel", "Paula", "Andrés",
    "Laura", "Fernando", "Isabel", "Raúl", "Clara"
]

# Lista de 20 apellidos
apellidos = [
    "García", "Fernández", "López", "Martínez", "Sánchez",
    "Pérez", "Gómez", "Martín", "Jiménez", "Ruiz",
    "Hernández", "Díaz", "Moreno", "Muñoz", "Álvarez",
    "Romero", "Alonso", "Gutiérrez", "Navarro", "Torres"
]

# Lista de 10 ciudades
ciudades = [
    "Madrid", "Barcelona", "Valencia", "Sevilla", "Bilbao",
    "Málaga", "Zaragoza", "Granada", "Toledo", "Salamanca"
]

# Lista de 5 categorías profesionales del sector programación
categorias_profesionales = [
    "Desarrollador Backend",
    "Desarrollador Frontend",
    "Ingeniero de Software",
    "Científico de Datos",
    "DevOps Engineer"
]

def obtener_conexion(nombre_database):
    # Anclamos rutas relativas a la carpeta del proyecto para que la
    # ejecución desde cualquier CWD no genere bases de datos nuevas.
    ruta = Path(nombre_database)
    if not ruta.is_absolute():
        ruta = BASE_DIR / ruta
    conn = sqlite3.connect(ruta)
    return conn

def crear_db(conn):
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS empleados(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        apellidos TEXT NOT NULL,
        categoria_profesional TEXT NOT NULL,
        ciudad TEXT NOT NULL,
        salario INTEGER NOT NULL
    );""")
    conn.commit()

def __insert(c: sqlite3.Cursor, empleado: Empleado):
    sql = """INSERT INTO empleados (nombre, apellidos, categoria_profesional, ciudad, salario)
    VALUES (?, ?, ?, ?, ?)"""
    c.execute(sql, (
        empleado.nombre,
        empleado.apellidos,
        empleado.categoria_profesional,
        empleado.ciudad,
        empleado.salario
    ))
    
def insert_all(conn: sqlite3.Connection, empleados: list[Empleado]):
    c = conn.cursor()
    for empleado in empleados:
        __insert(c, empleado=empleado)
    conn.commit()
    c.close()

if __name__ == "__main__":

    numero_registros = input(f'Número de registros ({NUMERO_REGISTROS_DEFAULT}):')
    nombre_database = input(f'Nombre de la base de datos ({NOMBRE_DATABASE}):')
    salario_minimo = input(f'Salario mínimo ({SALARIO_MINIMO_DEFAULT}):')
    salario_maximo = input(f'Salario máximo ({SALARIO_MAXIMO_DEFAULT}):')

    numero_registros = NUMERO_REGISTROS_DEFAULT if len(numero_registros)==0 else int(numero_registros)
    nombre_database = NOMBRE_DATABASE if len(nombre_database)==0 else nombre_database
    salario_minimo = SALARIO_MINIMO_DEFAULT if len(salario_minimo)==0 else int(salario_minimo)
    salario_maximo = SALARIO_MAXIMO_DEFAULT if len(salario_maximo)==0 else int(salario_maximo)

    inicio = time.perf_counter()

    conn = obtener_conexion(nombre_database)
    crear_db(conn)
    empleados = []
    for i in range(numero_registros):
        empleado = Empleado(
            nombre=random.choice(nombres),
            apellidos=random.choice(apellidos),
            categoria_profesional=random.choice(categorias_profesionales),
            ciudad=random.choice(ciudades),
            salario=random.randint(salario_minimo, salario_maximo)
        )        
        empleados.append(empleado)
    insert_all(conn, empleados)        
    
    # Cerramos la conexión
    conn.close()

    fin = time.perf_counter()
    print(f"Tiempo de ejecución: {fin - inicio:.6f} segundos")
