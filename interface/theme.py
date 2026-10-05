import flet as ft

ACENTO = "#7C9CFF"
ACENTO_2 = "#B58CFF"
TEXTO = "#F2F4FF"
TEXTO_SUAVE = "#A9B0CC"
OK = "#5EE6A8"
ERROR = "#FF6B81"
FONDO = ["#0B1020", "#141B3A", "#1E1038"]
WALPPAPER = "cinema-wallpaper.jpg" # Fondo usado para la ventana de inicio.

# Función que crea los orbes de fondo
def _orbe(color, tam, **pos):
    return ft.Container(
        width=tam, height=tam, **pos,
        gradient=ft.RadialGradient(colors=[color, "#00000000"]),
    )


# Función que crea el fondo de la aplicación
def fondo():
    return ft.Stack(
        expand=True,
        controls=[
            ft.Image(
                src=WALPPAPER,
                fit=ft.BoxFit.COVER,
                expand=True),
            ft.Container(
                expand=True,
                gradient=ft.LinearGradient(
                    begin=ft.Alignment.TOP_LEFT,
                    end=ft.Alignment.BOTTOM_RIGHT,
                    colors=["#55000000", "#99000000"],
                ),
            ),
        ],
    )



# Función que crea un contenedor con efecto de vidrio
def vidrio(content=None, radio=24, padding=20, **kw):
    return ft.Container(
        content=content,
        padding=padding,
        border_radius=radio,
        blur=ft.Blur(28, 28, ft.BlurTileMode.MIRROR),
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT,
            end=ft.Alignment.BOTTOM_RIGHT,
            colors=["#26FFFFFF", "#0DFFFFFF"],
        ),
        border=ft.Border.all(1, "#33FFFFFF"),
        shadow=ft.BoxShadow(blur_radius=40, color="#66000000", offset=ft.Offset(0, 12)),
        **kw,
    )


# Función que crea un botón con icono y texto
def boton(texto, icono, on_click, primario=False, color_texto=None):
    return ft.Container(
        on_click=on_click,
        ink=True,
        border_radius=14,
        padding=ft.Padding(left=18, top=12, right=18, bottom=12),
        blur=ft.Blur(12, 12, ft.BlurTileMode.MIRROR),
        bgcolor="#33FFFFFF" if primario else "#14FFFFFF",
        border=ft.Border.all(1, "#66FFFFFF" if primario else "#26FFFFFF"),
        shadow=ft.BoxShadow(blur_radius=16, color="#33000000", offset=ft.Offset(0, 4)),
        content=ft.Row(
            tight=True,
            spacing=8,
            controls=[
                ft.Icon(icono, size=18, color=color_texto or TEXTO),
                ft.Text(
                    texto,
                    color=color_texto or TEXTO,
                    weight=ft.FontWeight.W_600 if primario else ft.FontWeight.W_500,
                ),
            ],
        ),
    )


# Función que crea un campo de texto
def campo(label, **kw):
    return ft.TextField(
        label=label,
        filled=True,
        bgcolor="#20FFFFFF",
        border_radius=14,
        border_color="#33FFFFFF",
        focused_border_color=ACENTO,
        color=TEXTO,
        cursor_color=ACENTO,
        **kw,
    )


# Función que crea una etiqueta
def etiqueta(texto, activa=False, on_click=None):
    return ft.Container(
        on_click=on_click,
        padding=ft.Padding(left=12, top=5, right=12, bottom=5),
        border_radius=20,
        border=ft.Border.all(1, "#33FFFFFF"),
        bgcolor="#554A6BFF" if activa else "#14FFFFFF",
        content=ft.Text(texto, size=12, color=TEXTO),
    )
