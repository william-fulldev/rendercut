from dataclasses import dataclass
from datetime import date

@dataclass
class Pelicula:
    id: int
    titulo: str
    genero: str
    duracion: int
    anyo_estreno: int
    director: str

    def validar(self) -> None:
        for campo in ("titulo", "genero", "director"):
            if not str(getattr(self, campo)).strip():
                raise ValueError(f"El campo '{campo}' no puede estar vacio")
        if not 1 <= self.duracion <= 600:
            raise ValueError(f"La duración debe estar entre 1 y 600 minutos")
        if not 1880 <= self.anyo_estreno <= date.today().year + 5:
            raise ValueError(f"El año de estreno no es válido.")
