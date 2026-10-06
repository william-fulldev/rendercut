# Rendercut 🎬

**Tu próxima película, según tus gustos y el tiempo que tienes.**

Aplicación de escritorio para cinéfilos que permite organizar películas,
registrar valoraciones y obtener recomendaciones personalizadas entre
los títulos pendientes.

Desarrollada con **Python, Flet y SQLite**, con una interfaz oscura
de estilo glassmorphism.

![Biblioteca de Rendercut](docs/screenshots/biblioteca.jpg)

## Funcionalidades

- **Biblioteca:** añadir, editar y eliminar películas, buscar por título
  y filtrar por género y estado.
- **Diario de cine:** registrar películas pendientes, viendo o vistas,
  con valoración de 1 a 5, fecha de visionado y notas.
- **¿Qué veo hoy?:** recibir hasta tres recomendaciones ajustadas
  al tiempo disponible, con una explicación de cada sugerencia.
- **Estadísticas:** películas vistas, horas de metraje, valoración media,
  géneros favoritos y actividad mensual.
- **Almacenamiento local:** colección guardada en SQLite, sin necesidad
  de una cuenta.

## Recomendaciones explicables

El motor utiliza reglas, no inteligencia artificial: selecciona películas
pendientes que caben en el tiempo disponible y las ordena combinando
afinidad por género, afinidad por director y ajuste de duración.

Las afinidades se calculan a partir de tus valoraciones anteriores.
Si aún no has valorado películas, las sugerencias se basan en la duración
y los filtros seleccionados.

> «Dura 110 minutos y tienes 120; sueles puntuar bien la ciencia ficción
> (media 4,5/5)».

## Estadísticas

![Estadísticas de Rendercut](docs/screenshots/estadisticas.jpg)

## Desarrollo

- **Python:** modelo, validación y lógica de negocio.
- **Flet:** interfaz gráfica y componentes visuales reutilizables.
- **SQLite:** persistencia y migración de bases de datos existentes.
- **pytest:** pruebas de migración, validación y recomendación.

La interfaz, el acceso a datos y el recomendador están separados
para facilitar su mantenimiento y las pruebas.

```bash
pytest -q
```

Proyecto personal de portfolio en desarrollo. La documentación de
instalación y la versión empaquetada están pendientes.

**Próximas mejoras:** normalización de géneros y títulos duplicados,
carátulas y sinopsis, e importación y exportación de la colección.