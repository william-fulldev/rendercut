import sys
from pathlib import Path

# Aseguramos que la raíz del proyecto y back_logic estén en sys.path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))
if str(ROOT / "back_logic") not in sys.path:
    sys.path.append(str(ROOT / "back_logic"))
if str(ROOT / "interface") not in sys.path:
    sys.path.append(str(ROOT / "interface"))

from collections import Counter
from datetime import date

import flet as ft
import gestor_peliculas as gp
# pyrefly: ignore [missing-import]
from pelicula import Pelicula, ESTADOS
# pyrefly: ignore [missing-import]
from recomendador import recomendar
import theme as th


# CONSTANTES Y UTILIDADES COMUNES

ESTADO_TXT = {"pendiente": "Pendiente", "viendo": "Viendo", "vista": "Vista"}
ESTADO_ICONO = {
    "pendiente": ft.Icons.SCHEDULE,
    "viendo": ft.Icons.PLAY_CIRCLE,
    "vista": ft.Icons.CHECK_CIRCLE,
}
AMBAR = "#FFC857"  # Color de las estrellas


def _titulo(texto, sub=None):
    """Cabecera de cada pantalla: título grande y subtítulo opcional."""
    hijos = [ft.Text(texto, size=30, weight=ft.FontWeight.BOLD, color=th.TEXTO)]
    if sub:
        hijos.append(ft.Text(sub, color=th.TEXTO_SUAVE))
    return ft.Column(spacing=2, controls=hijos)


def _estrellas(valoracion):
    """Texto con estrellas: ★★★★☆. Si no hay nota, 'Sin valorar'."""
    if not valoracion:
        return "Sin valorar"
    return "★" * valoracion + "☆" * (5 - valoracion)


def _barra(etiqueta, valor, maximo, texto=None, ancho=320):
    """Barra horizontal para las estadísticas (sin librerías de gráficos)."""
    largo = max(6, int(ancho * valor / maximo)) if maximo else 6
    return ft.Row(
        spacing=12,
        controls=[
            ft.Container(width=150, content=ft.Text(etiqueta, color=th.TEXTO, size=13, max_lines=1)),
            ft.Container(width=largo, height=10, border_radius=5, bgcolor="#B3FFFFFF"),
            ft.Text(texto if texto is not None else str(valor), color=th.TEXTO_SUAVE, size=12),
        ],
    )


# VISTA: INICIO

def vista_inicio(page, conn, ir):
    pelis = gp.listar_peliculas(conn)
    vistas = [p for p in pelis if p.estado == "vista"]
    pendientes = [p for p in pelis if p.estado == "pendiente"]
    horas_vistas = sum(p.duracion for p in vistas) / 60

    def stat(icono, valor, etiqueta):
        """Tarjeta pequeña con un número grande y su descripción."""
        return th.vidrio(
            expand=True,
            content=ft.Row(
                controls=[
                    ft.Icon(icono, size=34, color=th.TEXTO),
                    ft.Column(
                        spacing=0,
                        controls=[
                            ft.Text(valor, size=22, weight=ft.FontWeight.BOLD, color=th.TEXTO),
                            ft.Text(etiqueta, size=12, color=th.TEXTO_SUAVE),
                        ],
                    ),
                ]
            ),
        )

    def fila(p):
        """Fila clicable de la lista de recientes."""
        return ft.Container(
            on_click=lambda e, i=p.id: ir("formulario", i),
            ink=True,
            border_radius=12,
            padding=10,
            content=ft.Row(
                controls=[
                    ft.Icon(ESTADO_ICONO[p.estado], size=18, color=th.TEXTO_SUAVE),
                    ft.Text(p.titulo, expand=True, color=th.TEXTO, weight=ft.FontWeight.W_600),
                    ft.Text(f"{p.director} · {p.anyo_estreno}", color=th.TEXTO_SUAVE, size=12),
                ]
            ),
        )

    recientes = sorted(pelis, key=lambda p: p.id, reverse=True)[:6]
    if recientes:
        bloque = ft.Column(controls=[fila(p) for p in recientes])
    else:
        bloque = ft.Column(
            controls=[
                ft.Text("Tu biblioteca está vacía.", color=th.TEXTO_SUAVE),
                th.boton("Añadir la primera", ft.Icons.ADD, lambda e: ir("formulario"), primario=True),
            ]
        )

    return ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        spacing=22,
        controls=[
            _titulo("Inicio", "Resumen de tu colección"),
            ft.Row(
                spacing=16,
                controls=[
                    stat(ft.Icons.MOVIE, str(len(pelis)), "películas en total"),
                    stat(ft.Icons.SCHEDULE, str(len(pendientes)), "pendientes"),
                    stat(ft.Icons.CHECK_CIRCLE, str(len(vistas)), "vistas"),
                    stat(ft.Icons.TIMER, f"{horas_vistas:.1f} h", "de cine visto"),
                ],
            ),
            th.boton("¿Qué veo hoy?", ft.Icons.AUTO_AWESOME, lambda e: ir("recomendar"), primario=True),
            th.vidrio(
                content=ft.Column(
                    controls=[
                        ft.Text("Añadidas recientemente", size=16, weight=ft.FontWeight.W_600, color=th.TEXTO),
                        bloque,
                    ]
                )
            ),
        ],
    )


# VISTA: BIBLIOTECA (búsqueda + filtros por estado y género)

def vista_biblioteca(page, conn, ir):
    filtros = {"genero": None, "estado": None}
    buscador = th.campo("Buscar por título", prefix_icon=ft.Icons.SEARCH, expand=True)
    chips_estado = ft.Row(wrap=True, spacing=8)
    chips_genero = ft.Row(wrap=True, spacing=8)
    rejilla = ft.Row(wrap=True, spacing=16, run_spacing=16)

    def tarjeta(p):
        """Tarjeta de cristal de una película."""
        return th.vidrio(
            width=250,
            on_click=lambda e, i=p.id: ir("formulario", i),
            ink=True,
            content=ft.Column(
                spacing=6,
                controls=[
                    ft.Row(
                        controls=[
                            th.etiqueta(p.genero),
                            ft.Icon(ESTADO_ICONO[p.estado], size=16, color=th.TEXTO_SUAVE),
                            ft.Text(ESTADO_TXT[p.estado], size=12, color=th.TEXTO_SUAVE),
                        ]
                    ),
                    ft.Text(p.titulo, size=18, weight=ft.FontWeight.BOLD, color=th.TEXTO, max_lines=2),
                    ft.Text(f"{p.director} · {p.anyo_estreno}", size=12, color=th.TEXTO_SUAVE),
                    ft.Row(
                        spacing=10,
                        controls=[
                            ft.Icon(ft.Icons.SCHEDULE, size=14, color=th.TEXTO_SUAVE),
                            ft.Text(f"{p.duracion} min", size=12, color=th.TEXTO_SUAVE),
                            ft.Text(_estrellas(p.valoracion), size=12, color=AMBAR),
                        ],
                    ),
                ],
            ),
        )

    def poner_filtro(clave, valor):
        filtros[clave] = valor
        refrescar()

    def construir():
        """Reconstruye chips y tarjetas según búsqueda y filtros (sin page.update)."""
        todas = gp.listar_peliculas(conn)
        generos = sorted({p.genero for p in todas})
        if filtros["genero"] not in generos:
            filtros["genero"] = None

        chips_estado.controls = [
            th.etiqueta("Todos los estados", filtros["estado"] is None, lambda e: poner_filtro("estado", None))
        ] + [
            th.etiqueta(ESTADO_TXT[s], filtros["estado"] == s, lambda e, s=s: poner_filtro("estado", s))
            for s in ESTADOS
        ]
        chips_genero.controls = [
            th.etiqueta("Todos los géneros", filtros["genero"] is None, lambda e: poner_filtro("genero", None))
        ] + [
            th.etiqueta(g, filtros["genero"] == g, lambda e, g=g: poner_filtro("genero", g))
            for g in generos
        ]

        pelis = gp.listar_peliculas(conn, buscador.value or "")
        if filtros["estado"]:
            pelis = [p for p in pelis if p.estado == filtros["estado"]]
        if filtros["genero"]:
            pelis = [p for p in pelis if p.genero == filtros["genero"]]
        rejilla.controls = [tarjeta(p) for p in pelis] or [
            ft.Text("No hay películas con esos filtros.", color=th.TEXTO_SUAVE)
        ]

    def refrescar(e=None):
        construir()
        page.update()

    buscador.on_change = refrescar
    construir()

    return ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        spacing=18,
        controls=[
            _titulo("Biblioteca", "Busca, filtra y abre una película para editarla"),
            ft.Row(controls=[buscador, th.boton("Nueva", ft.Icons.ADD, lambda e: ir("formulario"), primario=True)]),
            chips_estado,
            chips_genero,
            rejilla,
        ],
    )


# VISTA: FORMULARIO (nueva película / editar)

def vista_formulario(page, conn, ir, id_peli=None):
    editando = id_peli is not None
    actual = gp.obtener_pelicula(conn, id_peli) if editando else None
    if editando and actual is None:
        ir("biblioteca")
        return ft.Container()

    # Estado que cambia al pulsar chips/estrellas (no son campos de texto)
    sel = {
        "estado": actual.estado if actual else "pendiente",
        "valoracion": actual.valoracion if actual else None,
    }

    txt_titulo = th.campo("Título", width=420, value=actual.titulo if actual else "")
    txt_genero = th.campo("Género", width=420, value=actual.genero if actual else "")
    txt_duracion = th.campo(
        "Duración (min)", width=200, keyboard_type=ft.KeyboardType.NUMBER,
        value=str(actual.duracion) if actual else "",
    )
    txt_anyo = th.campo(
        "Año de estreno", width=200, keyboard_type=ft.KeyboardType.NUMBER,
        value=str(actual.anyo_estreno) if actual else "",
    )
    txt_director = th.campo("Director", width=420, value=actual.director if actual else "")
    txt_fecha = th.campo(
        "Fecha de visionado (AAAA-MM-DD)", width=300,
        value=(actual.fecha_visionado or "") if actual else "",
    )
    txt_notas = th.campo(
        "Notas personales", width=420, multiline=True, min_lines=3, max_lines=5,
        value=actual.notas if actual else "",
    )
    mensaje = ft.Text(size=13)

    # NUEVO: texto chiquito que me avisa de cómo se va a guardar el género que escribo
    aviso_genero = ft.Text(size=12, color=th.TEXTO_SUAVE)
    # NUEVO: fila donde van los chips con los géneros que ya tengo en la biblioteca
    chips_genero = ft.Row(wrap=True, spacing=8)

    fila_estados = ft.Row(spacing=8)
    fila_estrellas = ft.Row(spacing=2)
    # Este bloque (valoración + fecha) solo se ve si la película está 'vista'
    bloque_visto = ft.Column(
        spacing=12,
        controls=[ft.Text("Tu valoración", color=th.TEXTO_SUAVE, size=13), fila_estrellas, txt_fecha],
    )

    # NUEVO: calcula el texto del aviso mirando lo que hay escrito ahora mismo en el campo género
    def pintar_aviso_genero():
        # NUEVO: cojo lo escrito y le quito espacios de los lados (si es None, uso texto vacío)
        escrito = (txt_genero.value or "").strip()
        # NUEVO: le pregunto a la función de la 4.1 cómo debería quedar escrito
        bueno = gp.normalizar_genero(escrito)
        # NUEVO: solo aviso si hay algo escrito y se va a cambiar (si ya está bien, no molesto)
        if escrito and bueno and bueno != escrito:
            # NUEVO: este es el texto que verás debajo del campo
            aviso_genero.value = f"Se guardará como: {bueno}"
        else:
            # NUEVO: si no hay nada que corregir, dejo el aviso vacío
            aviso_genero.value = ""

    # NUEVO: esto se ejecuta al pulsar un chip de género
    def elegir_genero(g):
        # NUEVO: meto el género elegido en el campo de texto
        txt_genero.value = g
        # NUEVO: recalculo el aviso (con un género ya bueno se queda vacío)
        pintar_aviso_genero()
        # NUEVO: refresco la pantalla para que se vea el cambio
        page.update()

    # NUEVO: esto se ejecuta cada vez que escribo una letra en el campo género
    def al_escribir_genero(e):
        # NUEVO: recalculo el aviso con lo que llevo escrito
        pintar_aviso_genero()
        # NUEVO: refresco para que el aviso aparezca o desaparezca al momento
        page.update()

    # NUEVO: le digo al campo género que llame a la función de arriba cuando cambie su texto
    txt_genero.on_change = al_escribir_genero
    # NUEVO: saco los géneros distintos que ya hay guardados, ordenados de la A a la Z
    generos_existentes = sorted({p.genero for p in gp.listar_peliculas(conn)})
    # NUEVO: creo un chip por cada género; al pulsarlo llama a elegir_genero con ese género
    chips_genero.controls = [
        th.etiqueta(g, False, lambda e, g=g: elegir_genero(g)) for g in generos_existentes
    ]
    # NUEVO: calculo el aviso una vez al abrir (por si estoy editando una peli con el género mal escrito)
    pintar_aviso_genero()

    def elegir_estado(valor):
        sel["estado"] = valor
        if valor == "vista" and not txt_fecha.value:
            txt_fecha.value = date.today().isoformat()  # Fecha de hoy por defecto
        if valor != "vista":
            sel["valoracion"] = None
        refrescar_estado()

    def poner_nota(n):
        # Pulsar la misma estrella otra vez quita la valoración
        sel["valoracion"] = None if sel["valoracion"] == n else n
        refrescar_estado()

    def pintar_estado():
        """Redibuja chips de estado y estrellas según 'sel' (sin page.update)."""
        fila_estados.controls = [
            th.etiqueta(ESTADO_TXT[s], sel["estado"] == s, lambda e, s=s: elegir_estado(s))
            for s in ESTADOS
        ]
        fila_estrellas.controls = [
            ft.Container(
                on_click=lambda e, n=n: poner_nota(n),
                content=ft.Icon(
                    ft.Icons.STAR if sel["valoracion"] and n <= sel["valoracion"] else ft.Icons.STAR_BORDER,
                    color=AMBAR, size=30,
                ),
            )
            for n in range(1, 6)
        ]
        bloque_visto.visible = sel["estado"] == "vista"

    def refrescar_estado():
        pintar_estado()
        page.update()

    pintar_estado()

    def avisar(texto, color):
        mensaje.value = texto
        mensaje.color = color
        page.update()

    def leer() -> Pelicula:
        """Construye la Pelicula desde el formulario y la valida."""
        try:
            dur, anyo = int(txt_duracion.value), int(txt_anyo.value)
        except ValueError:
            raise ValueError("Duración y año deben ser números enteros.")
        es_vista = sel["estado"] == "vista"
        p = Pelicula(
            id_peli, txt_titulo.value, txt_genero.value, dur, anyo, txt_director.value,
            estado=sel["estado"],
            valoracion=sel["valoracion"] if es_vista else None,
            fecha_visionado=(txt_fecha.value.strip() or None) if es_vista else None,
            notas=txt_notas.value or "",
        )
        p.validar()
        return p

    def guardar(e):
        try:
            p = leer()
            if editando:
                if gp.actualizar_peli(conn, p) == 0:
                    return avisar("Esa película ya no existe.", th.ERROR)
                ir("biblioteca")
            else:
                gp.create_movie(conn, p)
                for c in (txt_titulo, txt_genero, txt_duracion, txt_anyo, txt_director, txt_fecha, txt_notas):
                    c.value = ""
                sel["estado"], sel["valoracion"] = "pendiente", None
                pintar_estado()
                # NUEVO: al limpiar el formulario, también limpio el aviso del género
                aviso_genero.value = ""
                avisar(f"'{p.titulo}' guardada correctamente.", th.OK)
        except ValueError as ex:
            avisar(str(ex), th.ERROR)

    def pedir_borrado(e):
        def borrar(ev):
            page.pop_dialog()
            gp.eliminar_pelicula(conn, id_peli=id_peli)
            ir("biblioteca")

        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("Eliminar película"),
                content=ft.Text(f"¿Seguro que quieres eliminar '{txt_titulo.value}'?"),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda ev: page.pop_dialog()),
                    ft.TextButton("Eliminar", on_click=borrar, style=ft.ButtonStyle(color=th.ERROR)),
                ],
            )
        )

    botones = [th.boton("Guardar", ft.Icons.SAVE, guardar, primario=True)]
    if editando:
        botones.append(th.boton("Eliminar", ft.Icons.DELETE, pedir_borrado, color_texto=th.ERROR))
    botones.append(th.boton("Cancelar", ft.Icons.CLOSE, lambda e: ir("biblioteca")))

    return ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        spacing=18,
        controls=[
            _titulo("Editar película" if editando else "Nueva película"),
            th.vidrio(
                content=ft.Column(
                    spacing=14,
                    controls=[
                        txt_titulo,
                        txt_genero,
                        # NUEVO: justo debajo del género van el aviso y los chips con los que ya usas
                        aviso_genero,
                        ft.Text("Géneros que ya usas:", color=th.TEXTO_SUAVE, size=12),
                        chips_genero,
                        ft.Row(controls=[txt_duracion, txt_anyo]),
                        txt_director,
                        ft.Text("Estado", color=th.TEXTO_SUAVE, size=13),
                        fila_estados,
                        bloque_visto,
                        txt_notas,
                        ft.Row(controls=botones),
                        mensaje,
                    ],
                )
            ),
        ],
    )

# VISTA: ESTADÍSTICAS

def vista_estadisticas(page, conn, ir):
    pelis = gp.listar_peliculas(conn)
    vistas = [p for p in pelis if p.estado == "vista"]

    if not vistas:
        return ft.Column(
            expand=True,
            spacing=18,
            controls=[
                _titulo("Estadísticas", "Se calculan con las películas que marques como vistas"),
                th.vidrio(content=ft.Text("Aún no has marcado ninguna película como vista.", color=th.TEXTO_SUAVE)),
            ],
        )

    valoradas = [p for p in vistas if p.valoracion]
    media = sum(p.valoracion for p in valoradas) / len(valoradas) if valoradas else None
    horas = sum(p.duracion for p in vistas) / 60

    # Géneros más vistos (top 6)
    por_genero = Counter(p.genero for p in vistas).most_common(6)
    max_genero = por_genero[0][1]

    # Películas vistas en cada uno de los últimos 6 meses
    y, m = date.today().year, date.today().month
    meses = []
    for _ in range(6):
        meses.append(f"{y:04d}-{m:02d}")
        m -= 1
        if m == 0:
            m, y = 12, y - 1
    meses.reverse()
    por_mes = Counter(p.fecha_visionado[:7] for p in vistas if p.fecha_visionado)
    max_mes = max([por_mes.get(k, 0) for k in meses] + [1])

    mejores = sorted(valoradas, key=lambda p: (-p.valoracion, p.titulo))[:5]

    def resumen(valor, etiqueta):
        return th.vidrio(
            expand=True,
            content=ft.Column(
                spacing=0,
                controls=[
                    ft.Text(valor, size=24, weight=ft.FontWeight.BOLD, color=th.TEXTO),
                    ft.Text(etiqueta, size=12, color=th.TEXTO_SUAVE),
                ],
            ),
        )

    return ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        spacing=20,
        controls=[
            _titulo("Estadísticas", "Tu actividad como espectador"),
            ft.Row(
                spacing=16,
                controls=[
                    resumen(str(len(vistas)), "películas vistas"),
                    resumen(f"{horas:.1f} h", "de metraje visto"),
                    resumen(f"{media:.1f} / 5" if media else "—", "valoración media"),
                ],
            ),
            th.vidrio(
                content=ft.Column(
                    spacing=10,
                    controls=[ft.Text("Géneros más vistos", size=16, weight=ft.FontWeight.W_600, color=th.TEXTO)]
                    + [_barra(g, n, max_genero) for g, n in por_genero],
                )
            ),
            th.vidrio(
                content=ft.Column(
                    spacing=10,
                    controls=[ft.Text("Vistas por mes", size=16, weight=ft.FontWeight.W_600, color=th.TEXTO)]
                    + [_barra(k, por_mes.get(k, 0), max_mes) for k in meses],
                )
            ),
            th.vidrio(
                content=ft.Column(
                    spacing=8,
                    controls=[ft.Text("Mejor valoradas", size=16, weight=ft.FontWeight.W_600, color=th.TEXTO)]
                    + [
                        ft.Row(
                            controls=[
                                ft.Text(p.titulo, expand=True, color=th.TEXTO),
                                ft.Text(_estrellas(p.valoracion), color=AMBAR),
                            ]
                        )
                        for p in mejores
                    ],
                )
            ),
        ],
    )


if __name__ == "__main__":
    from ventana_inicio import main
    ft.run(main, assets_dir=str(ROOT / "assets"))
