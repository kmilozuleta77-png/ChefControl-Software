"""
Inicialización del paquete chefcontrol_backend.
Se ejecuta ANTES que settings.py, por eso aquí se carga el .env y se elige
el driver MySQL antes de que Django importe el backend de base de datos.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Cargamos el .env aquí porque settings.py aún no se ha ejecutado
# (repetir load_dotenv en settings es seguro: no sobrescribe valores ya cargados)
load_dotenv(Path(__file__).resolve().parent.parent / '.env')

# Driver opcional: PyMySQL usa el TLS de Python (OpenSSL) en lugar de Schannel,
# lo que evita el error SEC_E_DECRYPT_FAILURE de mysqlclient en Windows con TiDB Cloud
if os.getenv('DB_DRIVER') == 'pymysql':
    import pymysql
    # Django exige mysqlclient >= 2.2.1: se declara esa versión para que acepte PyMySQL
    pymysql.version_info = (2, 2, 1, 'final', 0)
    pymysql.install_as_MySQLdb()
