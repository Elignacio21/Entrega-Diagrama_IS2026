from __future__ import annotations

from typing import TYPE_CHECKING

from qa_platform.errors import ErrorValidacion
from qa_platform.models.enums import TipoVoto

if TYPE_CHECKING:
    from qa_platform.models.publicacion import Publicacion
    from qa_platform.models.usuario import Usuario


class Voto:
    """Voto emitido por un Usuario sobre una Publicacion."""

    def __init__(self, usuario: Usuario, publicacion: Publicacion, tipo: TipoVoto):
        errores: dict[str, str] = {}
        if usuario is None:
            errores["usuario"] = "El voto debe tener un usuario"
        if publicacion is None:
            errores["publicacion"] = "El voto debe pertenecer a una publicación"
        if not isinstance(tipo, TipoVoto):
            errores["tipo"] = "El tipo de voto debe ser POSITIVO o NEGATIVO"
        if errores:
            raise ErrorValidacion(errores)

        self.usuario = usuario
        self.publicacion = publicacion
        self.tipo = tipo
        self.identificacion: int | None = None

    def __repr__(self):
        return f"<Voto {self.tipo.value} de {self.usuario!r} en {self.publicacion!r}>"