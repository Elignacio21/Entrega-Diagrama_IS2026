from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from dotenv import load_dotenv

from qa_platform.errors import ErrorValidacion
load_dotenv()

if TYPE_CHECKING:
    from qa_platform.models.pregunta import Pregunta


def _armar_prompt(p: Pregunta) -> str:
    etiquetas = ", ".join(e.nombre for e in p.etiquetas) or "ninguna"
    return (
        f"Categoría: {p.categoria.nombre}\n"
        f"Etiquetas: {etiquetas}\n"
        f"Título: {p.titulo}\n"
        f"Cuerpo: {p.cuerpo}\n\n"
        "Respondé de forma clara y didáctica para ayudar a un estudiante."
    )


class LLM(ABC):
    """Interfaz común para los proveedores de modelos de lenguaje (patrón Strategy)."""

    @abstractmethod
    def generarCuerpo(self, p: Pregunta) -> str:
        """Genera el cuerpo de la respuesta a partir de una Pregunta."""
        raise NotImplementedError(
            f"{type(self).__name__} debe implementar generarCuerpo()"
        )


class Gemini(LLM):
    """Implementación concreta de LLM para Google Gemini."""

    def __init__(
        self,
        api_key: str | None = None,
        modelo: str = "gemini-2.5-flash",
    ):
        self.api_key = api_key if api_key is not None else os.getenv("GEMINI_API_KEY", "")
        self.modelo = modelo

    def generarCuerpo(self, p: Pregunta) -> str:
        if p is None:
            raise ErrorValidacion({"pregunta": "La pregunta es obligatoria"})
        if not isinstance(self.api_key, str) or not self.api_key.strip():
            raise ErrorValidacion(
                {"api_key": "La clave GEMINI_API_KEY no está configurada"}
            )

        prompt = _armar_prompt(p)
        # Punto de integración con el SDK oficial de Google (google-genai) usando self.api_key y prompt
        return (
            f"[Gemini - {self.modelo}] Respuesta sugerida para '{p.titulo}': "
            f"revisá los conceptos fundamentales de {p.categoria.nombre}."
        )


class OpenIA(LLM):
    """Implementación concreta de LLM para OpenAI."""

    def __init__(
        self,
        api_key: str | None = None,
        modelo: str = "gpt-4o-mini",
    ):
        self.api_key = api_key if api_key is not None else os.getenv("OPENAI_API_KEY", "")
        self.modelo = modelo

    def generarCuerpo(self, p: Pregunta) -> str:
        if p is None:
            raise ErrorValidacion({"pregunta": "La pregunta es obligatoria"})
        if not isinstance(self.api_key, str) or not self.api_key.strip():
            raise ErrorValidacion(
                {"api_key": "La clave OPENAI_API_KEY no está configurada"}
            )

        prompt = _armar_prompt(p)
        # Punto de integración con el SDK oficial de OpenAI usando self.api_key y prompt
        return (
            f"[OpenIA - {self.modelo}] Respuesta sugerida para '{p.titulo}': "
            f"analizá el problema de {p.categoria.nombre} paso a paso."
        )


class ModeloLocal(LLM):
    """Implementación concreta de LLM para un modelo local (sin API key externa)."""

    def __init__(
        self,
        url: str | None = None,
        modelo: str = "llama3",
    ):
        self.url = url if url is not None else os.getenv("LOCAL_LLM_URL", "http://localhost:11434")
        self.modelo = modelo

    def generarCuerpo(self, p: Pregunta) -> str:
        if p is None:
            raise ErrorValidacion({"pregunta": "La pregunta es obligatoria"})

        prompt = _armar_prompt(p)
        # Punto de integración con servidor local (ej. Ollama) en self.url usando prompt
        return (
            f"[ModeloLocal - {self.modelo}] Respuesta sugerida para '{p.titulo}': "
            f"verificá los casos borde en {p.categoria.nombre}."
        )