from qa_platform.errors import ErrorValidacion
from qa_platform.extensions import db


class Categoria(db.Model):
    """Tema general al que pertenece una pregunta (por ejemplo, "Python").

    Ahora es una tabla. Dos categorías con el mismo nombre siguen siendo
    iguales (==), como cuando era un dataclass.
    """

    __tablename__ = "categoria"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)

    def __init__(self, nombre: str):
        if not isinstance(nombre, str) or not nombre.strip():
            raise ErrorValidacion(
                {"nombre": "El nombre de la categoría es obligatorio"}
            )
        self.nombre = nombre

    def __eq__(self, otro) -> bool:
        return isinstance(otro, Categoria) and self.nombre == otro.nombre

    def __hash__(self) -> int:
        return hash(self.nombre)

    def __repr__(self):
        return f"<Categoria {self.nombre!r}>"