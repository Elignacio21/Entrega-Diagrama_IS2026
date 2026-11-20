from flask_sqlalchemy import SQLAlchemy

# Instancia compartida: se crea acá y se vincula a la app en create_app().
# Así los modelos pueden importarla sin generar imports circulares.
db = SQLAlchemy()
