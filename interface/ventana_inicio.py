import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import flet as ft

import gestor_peliculas as gp
from interface import theme as th
from interface import vistas


# Función principal que se ejecuta al iniciar la aplicación
def main(page: ft.Page):
    # Conexión a la base de datos y creación/migración de tablas
    conn = gp.establecer_conexion()
    gp.crear_tablas(conn)

    # Configuración de la página (título, tema, fondo, tamaño)
    page.title = "Gestor de Películas"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = th.FONDO[0]
    page.padding = 0
    page.window.width = 1280
    page.window.height = 780

    # Contenedor donde se pinta la vista activa y diccionario de botones del menú
    contenido = ft.Container(expand=True, padding=ft.Padding(left=24, top=10, right=10, bottom=10))
    nav_items = {}

    # Resalta en el menú lateral la sección activa
    def pintar_nav(activo):
        for clave, item in nav_items.items():
            item.bgcolor = "#334A6BFF" if clave == activo else None
            item.border = ft.Border.all(1, "#33FFFFFF") if clave == activo else None

    # Navega entre vistas. Para añadir una sección nueva: otro 'elif' aquí
    def ir(destino, id_peli=None):
        if destino == "inicio":
            contenido.content = vistas.vista_inicio(page, conn, ir)
        elif destino == "biblioteca":
            contenido.content = vistas.vista_biblioteca(page, conn, ir)
        elif destino == "recomendar":
            contenido.content = vistas.vista_recomendar(page, conn, ir)
        elif destino == "estadisticas":
            contenido.content = vistas.vista_estadisticas(page, conn, ir)
        else:
            contenido.content = vistas.vista_formulario(page, conn, ir, id_peli)
        # Editar una película resalta 'Biblioteca' en el menú
        pintar_nav("biblioteca" if destino == "formulario" and id_peli else destino)
        page.update()

    # Crea cada botón del menú lateral
    def item(clave, icono, texto):
        c = ft.Container(
            on_click=lambda e: ir(clave),
            ink=True,
            border_radius=14,
            padding=ft.Padding(left=14, top=12, right=14, bottom=12),
            content=ft.Row(
                controls=[ft.Icon(icono, size=20, color=th.TEXTO), ft.Text(texto, color=th.TEXTO)]
            ),
        )
        nav_items[clave] = c
        return c

    # Menú lateral con efecto cristal
    sidebar = th.vidrio(
        width=240,
        content=ft.Column(
            spacing=8,
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.MOVIE_FILTER, color=th.ACENTO, size=28),
                        ft.Text("Rendercut", size=22, weight=ft.FontWeight.BOLD, color=th.TEXTO),
                    ]
                ),
                ft.Container(height=14),
                item("inicio", ft.Icons.HOME, "Inicio"),
                item("biblioteca", ft.Icons.VIDEO_LIBRARY, "Biblioteca"),
                item("recomendar", ft.Icons.AUTO_AWESOME, "¿Qué veo hoy?"),
                item("estadisticas", ft.Icons.INSIGHTS, "Estadísticas"),
                item("formulario", ft.Icons.ADD_CIRCLE_OUTLINE, "Nueva película"),
            ],
        ),
    )

    # Fondo (wallpaper) + menú lateral + contenido
    page.add(
        ft.Stack(
            expand=True,
            controls=[
                th.fondo(),
                ft.Container(
                    expand=True,
                    padding=20,
                    content=ft.Row(expand=True, controls=[sidebar, contenido]),
                ),
            ],
        )
    )

    # Vista inicial
    ir("inicio")


if __name__ == "__main__":
    # assets_dir apunta a la carpeta 'assets' de la raíz del proyecto
    RAIZ = Path(__file__).resolve().parent.parent
    ft.run(main, assets_dir=str(RAIZ / "assets"))