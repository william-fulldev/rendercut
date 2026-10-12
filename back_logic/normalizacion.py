"""Normalización de géneros y detección de títulos duplicados."""

import re  # Sirve para buscar y reemplazar patrones de texto
import unicodedata  # Para trabajar con caracteres Unicode (tildes, símbolos...)

# Lista de géneros "oficiales": así queremos verlos escritos siempre
GENEROS = [  # Ejemplo: si el usuario escribe "accion", se guardará "Acción"
    "Acción", "Animación", "Aventura", "Bélico", "Ciencia ficción",
    "Comedia", "Crimen", "Drama", "Fantasía", "Misterio",
    "Musical", "Suspense", "Terror", "Thriller", "Western",
]

# Alias: otras formas habituales de escribir un género, ya convertidas en "clave"
ALIAS = {  # Diccionario: clave del alias - género oficial
    "sci fi": "Ciencia ficción",  # "Sci-Fi" pasa a "sci fi" tras limpiar el guion
    "scifi": "Ciencia ficción",
    "ciencia ficcion": "Ciencia ficción",
    "belica": "Bélico",
    "accion y aventura": "Acción",
} 


def clave(texto: str) -> str:  # Convierte un texto en una "clave" comparable
    """'Ciencia Ficción' -> 'ciencia ficcion'."""
    texto = unicodedata.normalize("NFD", texto)  # Separa cada letra de su tilde: "ó" pasa a "o" + "´"
    texto = "".join(  # Une de nuevo los caracteres que nos quedemos
        c for c in texto if unicodedata.category(c) != "Mn"  # Descarta los caracteres de categoría "Mn" (las tildes sueltas)
    )
    texto = re.sub(r"[\W_]+", " ", texto.lower())  # Minúsculas y todo lo que no sea letra/número pasa a un espacio
    return texto.strip()  # Quita los espacios sobrantes del principio y del final


# Diccionario clave - género oficial, construido a partir de la lista GENEROS
CLAVE_A_GENERO = {clave(g): g for g in GENEROS}  # Ejemplo: {"ciencia ficcion": "Ciencia ficción", ...}
CLAVE_A_GENERO.update(ALIAS)  # Añade los alias al mismo diccionario


def normalizar_genero(genero: str) -> str:  # Devuelve el género escrito de forma estándar
    """'CIENCIA FICCION' -> 'Ciencia ficción'."""
    k = clave(genero)  # Calcula la clave del texto recibido
    if not k:  # Si la clave está vacía (el texto era vacío o solo símbolos)...
        return ""  # ...devuelve vacío y deja que validar() lo rechace
    if k in CLAVE_A_GENERO:  # Si la clave coincide con un género oficial o un alias...
        return CLAVE_A_GENERO[k]  # ...devuelve su forma oficial
    limpio = " ".join(genero.split())  # Género desconocido: colapsa espacios repetidos ("a   b" -> "a b")
    return limpio[:1].upper() + limpio[1:].lower()  # Primera letra en mayúscula y el resto en minúscula


def buscar_duplicado(peliculas, titulo: str, anyo: int, id_ignorar=None):  # Busca una película equivalente
    """Devuelve la película existente con mismo título (según clave) y año, o None."""  # Qué devuelve
    k = clave(titulo)  # Clave del título que queremos comprobar
    for p in peliculas:  # Recorremos las películas ya guardadas
        mismo_id = p.id == id_ignorar  # True si es la misma película que estamos editando
        if not mismo_id and p.anyo_estreno == anyo and clave(p.titulo) == k:  # Otra película, mismo año y misma clave
            return p  # La encontramos: la devuelve
    return None  # Si el bucle termina sin coincidencias, no hay duplicado
    