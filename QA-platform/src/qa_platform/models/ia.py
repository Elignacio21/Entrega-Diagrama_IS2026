from __future__ import annotations

from typing import TYPE_CHECKING

from qa_platform.errors import ErrorValidacion
from qa_platform.extensions import db
from qa_platform.models.autor import Autor
from qa_platform.models.llm import LLM, ModeloLocal
from qa_platform.models.respuesta import Respuesta

if TYPE_CHECKING:
    from qa_platform.models.pregunta import Pregunta


class IA(Autor):
    """Autor automático que delega la generación del texto a una estrategia LLM."""

    __tablename__ = "ia"

    identificacion = db.Column(
        db.Integer,
        db.ForeignKey("autor.identificacion"),
        primary_key=True,
    )

    __mapper_args__ = {"polymorphic_identity": "ia"}

    def __init__(self, llm: LLM | None = None, identificacion: int | None = None):
        proveedor = llm if llm is not None else ModeloLocal()
        if not isinstance(proveedor, LLM):
            raise ErrorValidacion({"llm": "El proveedor debe implementar la interfaz LLM"})

        self._llm: LLM = proveedor
        if identificacion is not None:
            self.identificacion = identificacion

    @property
    def llm(self) -> LLM:
        return self._llm

    @llm.setter
    def llm(self, proveedor: LLM) -> None:
        if not isinstance(proveedor, LLM):
            raise ErrorValidacion({"llm": "El proveedor debe implementar la interfaz LLM"})
        self._llm = proveedor

    def crearRespuesta(self, p: Pregunta, cuerpo: str | None = None) -> Respuesta:
        """Crea y registra una Respuesta en la Pregunta usando la estrategia LLM configurada."""
        if p is None:
            raise ErrorValidacion({"pregunta": "La pregunta es obligatoria"})

        texto = (
            cuerpo.strip()
            if isinstance(cuerpo, str) and cuerpo.strip()
            else self._llm.generarCuerpo(p)
        )
        respuesta = Respuesta(texto, pregunta=p, autor=self)
        p.agregar_respuesta(respuesta)
        return respuesta

    def __repr__(self):
        return f"<IA {type(self._llm).__name__}>"