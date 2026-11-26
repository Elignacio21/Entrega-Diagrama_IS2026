from qa_platform.errors import ErrorValidacion
from qa_platform.extensions import db


class Etiqueta(db.Model):
    """Palabra clave que describe una pregunta (por ejemplo, "flask")."""

    __tablename__ = "etiqueta"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)

    def __init__(self, nombre: str):
        if not isinstance(nombre, str) or not nombre.strip():
            raise ErrorValidacion(
                {"nombre": "El nombre de la etiqueta es obligatorio"}
            )
        self.nombre = nombre

    def __eq__(self, otro) -> bool:
        return isinstance(otro, Etiqueta) and self.nombre == otro.nombre

    def __hash__(self) -> int:
        return hash(self.nombre)

    def __repr__(self):
        return f"<Etiqueta {self.nombre!r}>"