from dataclasses import dataclass

from qa_platform.errors import ErrorValidacion


@dataclass(frozen=True)
class Categoria:
    """Tema general al que pertenece una pregunta (por ejemplo, "Python").

    frozen=True la hace inmutable. Dos categorías con el mismo nombre son
    iguales (==), porque @dataclass compara por los atributos.
    """

    nombre: str

    def __post_init__(self):
        if not isinstance(self.nombre, str) or not self.nombre.strip():
            raise ErrorValidacion(
                {"nombre": "El nombre de la categoría es obligatorio"}
            )