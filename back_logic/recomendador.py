from pelicula import Pelicula


def _afinidad(vistas, atributo, valor):
    notas = [p.valoracion for p in vistas if getattr(p, atributo) == valor and p.valoracion]
    if not notas:
        return 0.0, None
    media = sum(notas) / len(notas)
    return (media - 3) / 2, media

# Función que recomienda películas según las valoraciones y gustos del usuario.
def recomendar(peliculas: list[Pelicula], minutos: int, genero: str | None = None, n: int = 3):
    if minutos <= 0:
        return []
    # Películas ya vistas
    vistas = [p for p in peliculas if p.estado == "vista"]
    # Películas candidatas (pendientes, duración <= minutos y género opcional)
    candidatas = [
        p for p in peliculas
        if p.estado == "pendiente" and p.duracion <= minutos and (genero is None or p.genero == genero)
    ]
    # Recomendaciones por género y director
    puntuadas = []
    for p in candidatas:
        a_gen, m_gen = _afinidad(vistas, "genero", p.genero)
        a_dir, m_dir = _afinidad(vistas, "director", p.director)
        puntuacion = 2 * a_gen + a_dir + p.duracion / minutos
        motivos = [f"dura {p.duracion} min y tienes {minutos}"]
        if m_gen is not None and a_gen > 0:
            motivos.append(f"sueles puntuar bien el género {p.genero} (media {m_gen:.1f}/5)")
        if m_dir is not None and a_dir > 0:
            motivos.append(f"te gustó otra de {p.director} (media {m_dir:.1f}/5)")
        puntuadas.append((puntuacion, p, "; ".join(motivos)))
    puntuadas.sort(key=lambda t: (-t[0], t[1].titulo))
    return [(p, motivo) for _, p, motivo in puntuadas[:n]]