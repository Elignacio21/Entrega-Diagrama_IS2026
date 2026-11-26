from __future__ import annotations

from typing import TYPE_CHECKING

from qa_platform.errors import ErrorValidacion
from qa_platform.extensions import db
from qa_platform.models.autor import Autor
from qa_platform.models.llm import LLM
from qa_platform.models.respuesta import Respuesta

if TYPE_CHECKING:
    from qa_platform.models.pregunta import Pregunta


class IA(Autor):
    """Agente de IA que responde preguntas usando una estrategia LLM inyectada."""

    __tablename__ = "ia"

    identificacion = db.Column(
        db.Integer,
        db.ForeignKey("autor.identificacion"),
        primary_key=True,
    )

    __mapper_args__ = {"polymorphic_identity": "ia"}

    def __init__(self, modelo: LLM | None = None):
        self.modelo: LLM | None = None
        if modelo is not None:
            self.setLLM(modelo)

    def setLLM(self, m: LLM) -> None:
        """Asigna o cambia el proveedor de LLM en tiempo de ejecución."""
        if not isinstance(m, LLM):
            raise ErrorValidacion({"modelo": "El proveedor debe implementar la interfaz LLM"})
        self.modelo = m

    def generarCuerpoRespuesta(self, p: Pregunta) -> str:
        """Genera el cuerpo de la respuesta delegando en el LLM configurado."""
        if p is None:
            raise ErrorValidacion({"pregunta": "La pregunta es obligatoria"})
        if self.modelo is None:
            raise ErrorValidacion({"modelo": "La IA no tiene un proveedor LLM configurado"})
        return self.modelo.generarCuerpo(p)

    def crearRespuesta(self, p: Pregunta, cuerpo: str | None = None) -> Respuesta:
        """Crea y registra una Respuesta en la Pregunta, igual que un Usuario."""
        if p is None:
            raise ErrorValidacion({"pregunta": "La pregunta es obligatoria"})

        texto = (
            cuerpo.strip()
            if isinstance(cuerpo, str) and cuerpo.strip()
            else self.generarCuerpoRespuesta(p)
        )
        respuesta = Respuesta(texto, pregunta=p, autor=self)
        p.agregar_respuesta(respuesta)
        return respuesta

    def __repr__(self):
        proveedor = type(self.modelo).__name__ if self.modelo is not None else "sin LLM"
        return f"<IA ({proveedor})>"