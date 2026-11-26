import sqlite3

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine

# Instancia compartida: se crea acá y se vincula a la app en create_app().
# Así los modelos pueden importarla sin generar imports circulares.
db = SQLAlchemy()


@event.listens_for(Engine, "connect")
def _activar_claves_foraneas(dbapi_connection, _registro):
    """SQLite NO hace cumplir las claves foráneas por defecto: se activan acá.

    Sin esto, una FK inválida (por ejemplo una respuesta a una pregunta que no
    existe) se guardaría sin error. PostgreSQL ya las exige de fábrica.
    """
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()