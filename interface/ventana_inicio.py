import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import flet as ft

import gestor_peliculas as gp
from interface import theme as th
from interface import vistas

# Función principal que se ejecuta al iniciar la aplicación
def main(page: ft.Page):
    # Conexión a la base de datos y creación de tablas
    conn = gp.establecer_conexion()
    gp.crear_tablas(conn)

    # Configuración de la página (título, tema, fondo, tamaño)
    page.title = "Gestor de Películas"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = th.FONDO[0]
    page.padding = 0
    page.window.width = 1280
    page.window.height = 780

    # Contenedor principal y diccionario para el sidebar
    contenido = ft.Container(expand=True, padding=ft.Padding(left=24, top=10, right=10, bottom=10))
    nav_items = {}

    # Función que pinta el sidebar
    def pintar_nav(activo):
        for clave, item in nav_items.items():
            item.bgcolor = "#334A6BFF" if clave == activo else None
            item.border = ft.Border.all(1, "#33FFFFFF") if clave == activo else None

    # Función que navega entre vistas y actualiza el contenido
    def ir(destino, id_peli=None):
        if destino == "inicio":
            contenido.content = vistas.vista_inicio(page, conn, ir)
        elif destino == "biblioteca":
            contenido.content = vistas.vista_biblioteca(page, conn, ir)
        else:
            contenido.content = vistas.vista_formulario(page, conn, ir, id_peli)
        pintar_nav("biblioteca" if destino == "formulario" and id_peli else destino)
        page.update()

    # Función que crea cada item del sidebar
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
    
    # Sidebar con el menú de navegación con iconos y textos
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
                item("formulario", ft.Icons.ADD_CIRCLE_OUTLINE, "Nueva película"),
            ],
        ),
    )

    # Función que añade el sidebar y el contenido a la página
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
    
    # Navega a la vista de inicio al iniciar la aplicación
    ir("inicio")

if __name__ == "__main__":
    ft.run(main)