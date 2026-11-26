from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from typing import TYPE_CHECKING

from qa_platform.errors import ErrorValidacion
from qa_platform.models.categoria import Categoria
from qa_platform.models.etiqueta import Etiqueta
from qa_platform.models.publicacion import Publicacion
from qa_platform.models.respuesta import Respuesta

if TYPE_CHECKING:
    # Solo para anotaciones: usuario.py importa a este módulo, y así se evita
    # un import circular.
    from qa_platform.models.usuario import Usuario


def _es_texto_valido(valor) -> bool:
    return isinstance(valor, str) and bool(valor.strip())


class Pregunta(Publicacion):
    """Pregunta publicada en la plataforma.

    Tiene un autor (Usuario), exactamente una Categoria (obligatoria), cero
    o más Etiquetas y cero o más Respuestas. Si los datos no son válidos, no
    se crea y se lanza ErrorValidacion con TODOS los errores encontrados.
    """

    def __init__(
        self,
        titulo: str,
        cuerpo: str,
        categoria: Categoria,
        autor: Usuario,
        etiquetas: Iterable[Etiqueta] = (),
        fecha: datetime | None = None,
    ):
        etiquetas = tuple(etiquetas or ())

        errores = self.validar_textos(titulo, cuerpo)
        if not isinstance(categoria, Categoria):
            errores["categoria"] = "La categoría es obligatoria"
        if autor is None:
            errores["autor"] = "La pregunta debe tener un autor"
        if not all(isinstance(etiqueta, Etiqueta) for etiqueta in etiquetas):
            errores["etiquetas"] = "Cada etiqueta debe ser una Etiqueta"
        if errores:
            raise ErrorValidacion(errores)

        super().__init__(cuerpo.strip(), fecha)
        self.titulo = titulo.strip()
        self.autor = autor
        self.categoria = categoria  # pasa por el setter, que valida
        self._etiquetas: list[Etiqueta] = []
        for etiqueta in etiquetas:
            self.agregar_etiqueta(etiqueta)
        self._respuestas: list[Respuesta] = []
        # Lo asigna el servicio al guardarla (igual que con los usuarios).
        # Mientras no esté guardada vale None.
        self.identificacion: int | None = None

    @staticmethod
    def validar_textos(titulo, cuerpo) -> dict[str, str]:
        """Errores del título y el cuerpo (vacío si ambos son válidos).

        Es estática para que el servicio pueda reutilizarla y juntar sus
        errores con los de otros campos antes de crear la pregunta.
        """
        errores: dict[str, str] = {}
        if not _es_texto_valido(titulo):
            errores["titulo"] = "El título es obligatorio"
        if not _es_texto_valido(cuerpo):
            errores["cuerpo"] = "El cuerpo es obligatorio"
        return errores

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

    @property
    def respuestas(self) -> tuple[Respuesta, ...]:
        """Respuestas de la pregunta (solo lectura; 0..*).

        Se agregan con agregar_respuesta, normalmente a través de
        Autor.crearRespuesta().
        """
        return tuple(self._respuestas)

    @property
    def respuesta_aceptada(self) -> Respuesta | None:
        """La respuesta aceptada de la pregunta, o None si todavía no hay."""
        for respuesta in self._respuestas:
            if respuesta.esAceptada:
                return respuesta
        return None

    def agregar_respuesta(self, respuesta: Respuesta) -> None:
        if not isinstance(respuesta, Respuesta):
            raise ErrorValidacion({"respuesta": "Debe ser una Respuesta"})
        # Toda respuesta pertenece a UNA única pregunta: la que declara ella.
        if respuesta.pregunta is not self:
            raise ErrorValidacion(
                {"respuesta": "La respuesta pertenece a otra pregunta"}
            )
        if respuesta not in self._respuestas:
            self._respuestas.append(respuesta)

    def __repr__(self):
        return f"<Pregunta {self.titulo!r}>"