from dataclasses import dataclass
from datetime import date

# Estados posibles de una película. Se importa desde otros archivos
# (interface/vistas.py), así que debe estar a nivel de módulo, sin sangría.
ESTADOS = ("pendiente", "viendo", "vista")


@dataclass
class Pelicula:
    # Campos obligatorios
    id: int | None
    titulo: str
    genero: str
    duracion: int
    anyo_estreno: int
    director: str
    # Campos de la Fase 3 (con valor por defecto)
    estado: str = "pendiente"
    valoracion: int | None = None
    fecha_visionado: str | None = None
    notas: str = ""

    def validar(self) -> None:
        """Lanza ValueError con un mensaje claro si algún dato no es válido."""
        # Textos obligatorios
        for campo in ("titulo", "genero", "director"):
            if not str(getattr(self, campo)).strip():
                raise ValueError(f"El campo '{campo}' no puede estar vacío.")
        # Duración y año con límites razonables
        if not 1 <= self.duracion <= 600:
            raise ValueError("La duración debe estar entre 1 y 600 minutos.")
        if not 1888 <= self.anyo_estreno <= date.today().year + 5:
            raise ValueError("El año de estreno no es válido.")
        # Estado permitido
        if self.estado not in ESTADOS:
            raise ValueError("Estado no válido.")
        # Solo se puede valorar una película vista, de 1 a 5
        if self.valoracion is not None:
            if self.estado != "vista":
                raise ValueError("Solo puedes valorar películas vistas.")
            if not 1 <= self.valoracion <= 5:
                raise ValueError("La valoración debe estar entre 1 y 5.")
        # La fecha, si existe, debe ser AAAA-MM-DD
        if self.fecha_visionado:
            try:
                date.fromisoformat(self.fecha_visionado)
            except ValueError:
                raise ValueError("La fecha debe tener el formato AAAA-MM-DD.")