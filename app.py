import gestor_peliculas as gp

if __name__=='__main__':
    conn=gp.establecer_conexion()
    gp.crear_tablas(conn)
    gp.menu_principal(conn)
    gp.cerrar_conexion(conn)