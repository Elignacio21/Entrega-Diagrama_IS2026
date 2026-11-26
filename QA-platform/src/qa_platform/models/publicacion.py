from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from qa_platform.errors import ErrorValidacion
from qa_platform.models.enums import TipoVoto

if TYPE_CHECKING:
    from qa_platform.models.voto import Voto


def _es_texto_valido(valor) -> bool:
    return isinstance(valor, str) and bool(valor.strip())


class Publicacion:
    """Clase base para publicaciones votables (Pregunta y Respuesta)."""

    def __init__(self, cuerpo: str, fecha: datetime | None = None):
        if not _es_texto_valido(cuerpo):
            raise ErrorValidacion({"cuerpo": "El cuerpo es obligatorio"})

        self.cuerpo = cuerpo.strip()
        self.fecha = fecha if fecha is not None else datetime.now()
        self._votos: list[Voto] = []

    @property
    def votos(self) -> tuple[Voto, ...]:
        return tuple(self._votos)

    def agregar_voto(self, voto: Voto) -> None:
        from qa_platform.models.voto import Voto

        if not isinstance(voto, Voto):
            raise ErrorValidacion({"voto": "Debe ser un Voto"})
        if voto.publicacion is not self:
            raise ErrorValidacion(
                {"voto": "El voto pertenece a otra publicación"}
            )
        if any(v.usuario is voto.usuario for v in self._votos):
            raise ErrorValidacion(
                {"voto": "El usuario ya votó esta publicación"}
            )
        if voto not in self._votos:
            self._votos.append(voto)

    def calcularPuntuacion(self) -> int:
        """Devuelve votos POSITIVO menos NEGATIVO (0 si no hay votos)."""
        positivos = sum(1 for v in self._votos if v.tipo == TipoVoto.POSITIVO)
        negativos = sum(1 for v in self._votos if v.tipo == TipoVoto.NEGATIVO)
        return positivos - negativos