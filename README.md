# Movie DB (Gestor de Películas) 🎬

Aplicación en Python para la gestión de bases de datos de películas con SQLite y soporte de interfaz gráfica con Flet y modo consola interactivo.

## 🚀 Características

- **Base de Datos SQLite**: Almacenamiento local de películas (`bbdd_peliculas.db`) con campos como título, género, duración, año de estreno y director.
- **Interfaz Gráfica (Flet)**: UI moderna para ver el listado, registrar nuevas películas, consultar/modificar registros existentes y eliminar películas.
- **Modo Consola (CLI)**: Menú interactivo por terminal para realizar operaciones CRUD completas.
- **Generador de Datos**: Módulo para generación y pruebas de rendimiento en bases de datos SQLite.

## 📁 Estructura del Proyecto

```text
├── app.py                     # Punto de entrada para ejecución por terminal (CLI)
├── bbdd_peliculas.db          # Base de datos SQLite
├── data_generator_db.py       # Generador de datos y benchmarks
├── gestor_peliculas.py        # Lógica CRUD y conexión a la base de datos
├── pelicula.py                # Modelo de datos / Clase Pelicula
├── interface/
│   └── ventana_inicio.py      # Interfaz gráfica de usuario con Flet
└── README.md
```

## 🛠️ Instalación y Uso

### Requisitos previos
- Python 3.10+
- `flet` (para la interfaz gráfica)

### Ejecución

1. **Modo Interfaz Gráfica:**
   ```bash
   python interface/ventana_inicio.py
   ```

2. **Modo Consola:**
   ```bash
   python app.py
   ```
