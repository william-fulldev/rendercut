import sys
from pathlib import Path

# 1. Primero añadimos la carpeta 'bbdd' al sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# 2. Después importamos los módulos
import flet as ft
from pelicula import Pelicula
import gestor_peliculas as gp
import data_generator_db as dg



def main(page: ft.Page):
    
    # Inicializar la base de datos y la conexión
    conn = gp.establecer_conexion() # Conexión a la base de datos
    gp.crear_tablas(conn) # Crear las tablas si no existen
    
    # Configuración de la ventana
    page.title = "Gestor de Películas"
    page.window.width = 900
    page.window.height = 600
    page.padding = 20
    
    # Área principal donde se cambia el contenido
    area_contenido = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)

    # Componente para mostrar la información de la BD
    txt_info_db = ft.Text(
        value="Estado BD: Conectado", 
        size=12, 
        color=ft.Colors.GREY_400
    )

    # Eventos / Funciones

    # Ver películas -----
    def mostrar_vista_ver(e):
        area_contenido.controls.clear()
        peliculas = gp.consultar_peli(conn, "")
        filas_pelis = []
        for peli in peliculas:
            filas_pelis.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(peli[0])),  #ID
                        ft.DataCell(ft.Text(peli[1])),  #Titulo
                        ft.DataCell(ft.Text(peli[2])),  #Genero
                        ft.DataCell(ft.Text(f"{peli[3]} min")),  #Duracion
                        ft.DataCell(ft.Text(str(peli[4]))),  #Año
                        ft.DataCell(ft.Text(peli[5]))  #Director
                    ]
                )
            )
        
        tabla_pelis = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Titulo")),
                ft.DataColumn(ft.Text("Genero")),
                ft.DataColumn(ft.Text("Duracion")),
                ft.DataColumn(ft.Text("Año")),
                ft.DataColumn(ft.Text("Director")),
            ],
            rows=filas_pelis, # Línea divisoria horizontal
        )
        area_contenido.controls.extend([ft.Text("Películas", size=22), tabla_pelis])
        page.update()

    # Insertar películas
    def mostrar_vista_insertar(e=None):
        area_contenido.controls.clear()

        txt_titulo = ft.TextField(label="Título", width=300)
        txt_genero = ft.TextField(label="Genero", width=300)
        txt_duracion = ft.TextField(label="Duración (min)", width=300, keyboard_type=ft.KeyboardType.NUMBER)
        txt_anyo = ft.TextField(label="Año", width=300, keyboard_type=ft.KeyboardType.NUMBER)
        txt_director = ft.TextField(label="Director", width=300)
        txt_mensaje = ft.Text(size=14)
        
        def guardar_peli(e):
            if not all([txt_titulo.value, txt_genero.value, txt_duracion.value, txt_anyo.value, txt_director.value]):
                txt_mensaje.value = "Completa todos los campos"
                txt_mensaje.color = ft.Colors.RED_400
                page.update()
                return

            try:
                nueva_peli = Pelicula(
                    id=None,
                    titulo=txt_titulo.value,
                    genero=txt_genero.value,
                    duracion=int(txt_duracion.value),
                    anyo_estreno=int(txt_anyo.value),
                    director=txt_director.value
                )
                gp.create_movie(conn, nueva_peli)
                txt_mensaje.value = f"La película '{txt_titulo.value}' se ha guardado correctamente"
                txt_mensaje.color = ft.Colors.GREEN_400

                txt_titulo.value = txt_genero.value = txt_duracion.value = txt_anyo.value = txt_director.value = ""
            except ValueError:
                txt_mensaje.value = "Duración y Año deben ser números enteros."
                txt_mensaje.color = ft.Colors.RED_400
            finally:
                page.update()
                
        area_contenido.controls.extend([
            ft.Text("Insertar Película", size=22, weight=ft.FontWeight.BOLD),
            txt_titulo, txt_genero, txt_duracion, txt_anyo, txt_director,
            ft.Button("Guardar", on_click=guardar_peli, icon=ft.Icons.SAVE),
            txt_mensaje
        ])
        page.update()

    # Modificar
    def mostrar_vista_modificar(e):
        area_contenido.controls.clear()

        # Controles
        txt_id = ft.TextField(label="ID a modificar", width=300, keyboard_type=ft.KeyboardType.NUMBER)
        txt_titulo = ft.TextField(label="Título", width=300)
        txt_genero = ft.TextField(label="Género", width=300)
        txt_duracion = ft.TextField(label="Duración (min)", width=300, keyboard_type=ft.KeyboardType.NUMBER)
        txt_anyo = ft.TextField(label="Año", width=300, keyboard_type=ft.KeyboardType.NUMBER)
        txt_director = ft.TextField(label="Director", width=300)
        txt_mensaje = ft.Text(size=14)

        # Función para cargar datos de la película seleccionada
        def cargar_datos_peli(e=None):
            try:
                pelicula = gp.consultar_peli_por_id(conn, int(txt_id.value))
                if pelicula:
                    txt_titulo.value = pelicula[1]
                    txt_genero.value = pelicula[2]
                    txt_duracion.value = str(pelicula[3])
                    txt_anyo.value = str(pelicula[4])
                    txt_director.value = pelicula[5]
                    txt_mensaje.value = "Datos cargados correctamente"
                    txt_mensaje.color = ft.Colors.GREEN_400
                else:
                    txt_mensaje.value = "No se encontró ninguna película con ese ID"
                    txt_mensaje.color = ft.Colors.RED_400
            except ValueError:
                txt_mensaje.value = "El ID debe ser un número entero"
                txt_mensaje.color = ft.Colors.RED_400
            except Exception as ex:
                txt_mensaje.value = f"Error al cargar película: {ex}"
                txt_mensaje.color = ft.Colors.RED_400
            page.update()

        # Función para guardar la modificación
        def guardar_modificacion(e):
            if not all([txt_id.value, txt_titulo.value, txt_genero.value, txt_duracion.value, txt_anyo.value, txt_director.value]):
                txt_mensaje.value = "Completa todos los campos"
                txt_mensaje.color = ft.Colors.RED_400
                page.update()
                return

            try:
                peli_actualizada = Pelicula(
                    id=int(txt_id.value),
                    titulo=txt_titulo.value,
                    genero=txt_genero.value,
                    duracion=int(txt_duracion.value),
                    anyo_estreno=int(txt_anyo.value),
                    director=txt_director.value
                )
                gp.actualizar_peli(conn, peli_actualizada)
                txt_mensaje.value = f"Película con ID {txt_id.value} modificada correctamente"
                txt_mensaje.color = ft.Colors.GREEN_400
            except ValueError:
                txt_mensaje.value = "ID, Duración y Año deben ser números enteros."
                txt_mensaje.color = ft.Colors.RED_400
            except Exception as ex:
                txt_mensaje.value = f"Error al modificar película: {ex}"
                txt_mensaje.color = ft.Colors.RED_400
            finally:
                page.update()

        area_contenido.controls.extend([
            ft.Text("Modificar Película", size=22, weight=ft.FontWeight.BOLD),
            txt_id,
            ft.Button("Cargar datos", on_click=cargar_datos_peli, icon=ft.Icons.DOWNLOAD),
            txt_titulo, txt_genero, txt_duracion, txt_anyo, txt_director,
            ft.Button("Guardar cambios", on_click=guardar_modificacion, icon=ft.Icons.SAVE, color=ft.Colors.ORANGE_400),
            txt_mensaje
        ])
        page.update()

    # Eliminar
    def mostrar_vista_eliminar(e):
        area_contenido.controls.clear()

        # Controles
        txt_titulo_eliminar = ft.TextField(label="Título o ID de la película a eliminar", width=300)
        txt_mensaje = ft.Text(size=14)

        def confirmar_eliminacion(e):
            valor = txt_titulo_eliminar.value.strip().lower()
            if not valor:
                txt_mensaje.value = "Introduce un id o un título."
                txt_mensaje.color = ft.Colors.RED_400
                page.update()
                return

            try:
                # Eliminar por id o por titulo
                if valor.isdigit():
                    resultado = gp.eliminar_pelicula(conn, id_peli=int(valor))
                else:
                    resultado = gp.eliminar_pelicula(conn, titulo=valor)

                if resultado > 0:
                    txt_mensaje.value = f"Película '{valor}' eliminada correctamente."
                    txt_mensaje.color = ft.Colors.GREEN_400
                    txt_titulo_eliminar.value = ""
                else:
                    txt_mensaje.value = f"No se encontró ninguna película con el criterio '{valor}'."
                    txt_mensaje.color = ft.Colors.RED_400
            except Exception as ex:
                txt_mensaje.value = f"Error al eliminar la película: {ex}"
                txt_mensaje.color = ft.Colors.RED_400
            finally:
                page.update()


        area_contenido.controls.extend([
            ft.Text("Eliminar Película", size=22, weight=ft.FontWeight.BOLD),
            txt_titulo_eliminar,
            ft.Button("Eliminar película", on_click=confirmar_eliminacion, icon=ft.Icons.DELETE, color=ft.Colors.RED_400),
            txt_mensaje
        ])
        page.update()

    def salir_app(e):
        page.window.close()
        sys.exit()

    # Menú lateral
    menu_lateral = ft.Container(
        width=220,
        padding=10,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        border_radius=10,
        content=ft.Column(
            controls=[
                ft.Text("Gestor DDBB", size=18, weight=ft.FontWeight.BOLD),
                txt_info_db,
                ft.Divider(), # Linea divisoria horizontal
                ft.Button("Ver películas", on_click=mostrar_vista_ver, width=180),
                ft.Button("Insertar película", width=180, on_click=mostrar_vista_insertar),
                ft.Button("Modificar película", width=180, on_click=mostrar_vista_modificar),
                ft.Button("Eliminar película", width=180, on_click=mostrar_vista_eliminar),
                ft.Divider(), # Linea divisoria horizontal
                ft.OutlinedButton("Salir", on_click=salir_app, width=180),
            ],
            spacing=12
        )
    )

    # Layout Principal - Menú a la izquierda y Contenido a la derecha
    layout_principal = ft.Row(
        controls=[
            menu_lateral,
            ft.VerticalDivider(width=1), # Línea divisoria vertical
            area_contenido
        ],
        expand=True
    )

    page.add(layout_principal)

if __name__ == "__main__":
    ft.run(main)