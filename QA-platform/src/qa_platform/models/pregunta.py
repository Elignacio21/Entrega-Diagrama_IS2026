from collections.abc import Iterable
from datetime import datetime

from qa_platform.errors import ErrorValidacion
from qa_platform.models.categoria import Categoria
from qa_platform.models.etiqueta import Etiqueta
from qa_platform.models.publicacion import Publicacion


class Pregunta(Publicacion):
    """Pregunta publicada en la plataforma.

    Tiene exactamente una Categoria (obligatoria) y cero o más Etiquetas.
    """

    def __init__(
        self,
        titulo: str,
        cuerpo: str,
        categoria: Categoria,
        etiquetas: Iterable[Etiqueta] = (),
        fecha: datetime | None = None,
    ):
        super().__init__(cuerpo, fecha)
        self.titulo = titulo
        self.categoria = categoria  # pasa por el setter, que valida
        self._etiquetas: list[Etiqueta] = []
        for etiqueta in etiquetas:
            self.agregar_etiqueta(etiqueta)

    @property
    def categoria(self) -> Categoria:
        return self._categoria

    @categoria.setter
    def categoria(self, categoria: Categoria) -> None:
        # Se valida acá (y no solo en el constructor) para que una pregunta
        # nunca pueda quedar sin categoría, ni al crearla ni después.
        if not isinstance(categoria, Categoria):
            raise ErrorValidacion({"categoria": "La categoría es obligatoria"})
        self._categoria = categoria

    @property
    def etiquetas(self) -> tuple[Etiqueta, ...]:
        """Etiquetas de la pregunta (solo lectura; se agregan con agregar_etiqueta)."""
        return tuple(self._etiquetas)

    def agregar_etiqueta(self, etiqueta: Etiqueta) -> None:
        if not isinstance(etiqueta, Etiqueta):
            raise ErrorValidacion({"etiquetas": "Cada etiqueta debe ser una Etiqueta"})
        if etiqueta not in self._etiquetas:
            self._etiquetas.append(etiqueta)

    def __repr__(self):
        return f"<Pregunta {self.titulo!r}>"