import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT / "back_logic") not in sys.path:
    sys.path.append(str(ROOT / "back_logic"))

import gestor_peliculas as gp

if __name__=='__main__':
    conn=gp.establecer_conexion()
    gp.crear_tablas(conn)
    gp.menu_principal(conn)
    gp.cerrar_conexion(conn)