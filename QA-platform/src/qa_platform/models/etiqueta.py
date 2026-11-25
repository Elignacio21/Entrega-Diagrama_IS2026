from dataclasses import dataclass

from qa_platform.errors import ErrorValidacion


@dataclass(frozen=True)
class Etiqueta:
    """Palabra clave que describe una pregunta (por ejemplo, "flask")."""

    nombre: str

    def __post_init__(self):
        if not isinstance(self.nombre, str) or not self.nombre.strip():
            raise ErrorValidacion({"nombre": "El nombre de la etiqueta es obligatorio"})