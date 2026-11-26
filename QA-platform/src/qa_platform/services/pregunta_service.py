from sqlalchemy.exc import SQLAlchemyError

from qa_platform.errors import ErrorValidacion
from qa_platform.extensions import db
from qa_platform.models.pregunta import Pregunta
from qa_platform.services.catalogo_service import (
    buscar_categoria,
    obtener_o_crear_etiqueta,
)
from qa_platform.services.usuario_service import buscar_usuario


def listar_preguntas() -> list[Pregunta]:
    """Devuelve las preguntas guardadas en la base."""
    return list(
        db.session.scalars(db.select(Pregunta).order_by(Pregunta.identificacion))
    )


def buscar_pregunta(pregunta_id) -> Pregunta | None:
    """Busca una pregunta por su identificacion; None si no existe."""
    # bool es un subtipo de int en Python: True == 1, y no debe valer como id.
    if isinstance(pregunta_id, bool) or not isinstance(pregunta_id, int):
        return None
    return db.session.get(Pregunta, pregunta_id)


def limpiar_preguntas() -> None:
    """Se mantiene solo para no romper tests viejos (ver usuario_service)."""


def _normalizar_etiquetas(nombres) -> tuple[list[str], str | None]:
    """Convierte una lista de textos en nombres de etiqueta (minúsculas, sin repetidos).

    Devuelve (nombres, mensaje_de_error). Si no se envía nada, no hay
    etiquetas: son opcionales. Todavía NO toca la base: las etiquetas se
    crean recién cuando el resto de los datos ya fue validado.
    """
    if nombres is None:
        return [], None

    es_lista_de_textos = isinstance(nombres, list) and all(
        isinstance(nombre, str) and nombre.strip() for nombre in nombres
    )
    if not es_lista_de_textos:
        return [], "Las etiquetas deben ser una lista de textos no vacíos"

    return list(dict.fromkeys(nombre.strip().lower() for nombre in nombres)), None


def crear_pregunta(autor_id, titulo, cuerpo, categoria, etiquetas=None) -> Pregunta:
    """Valida los datos, crea la pregunta del usuario y la guarda en la base.

    - autor_id: identificacion de un Usuario registrado.
    - categoria: nombre de una categoría del catálogo.
    - etiquetas: lista de nombres (opcional).

    La fecha de publicación y el identificador los fija el sistema; el
    cliente no puede elegirlos.

    Lanza ErrorValidacion con todos los errores encontrados.
    """
    errores = Pregunta.validar_textos(titulo, cuerpo)

    autor = buscar_usuario(autor_id)
    if autor is None:
        errores["autor"] = "El usuario no está registrado"

    categoria_encontrada = buscar_categoria(categoria)
    if categoria_encontrada is None:
        hay_texto = isinstance(categoria, str) and categoria.strip()
        errores["categoria"] = (
            "La categoría indicada no existe"
            if hay_texto
            else "La categoría es obligatoria"
        )

    nombres_etiquetas, error_etiquetas = _normalizar_etiquetas(etiquetas)
    if error_etiquetas:
        errores["etiquetas"] = error_etiquetas

    if errores:
        raise ErrorValidacion(errores)

    try:
        lista_etiquetas = [obtener_o_crear_etiqueta(n) for n in nombres_etiquetas]
        pregunta = autor.generarPregunta(
            titulo,
            cuerpo,
            categoria=categoria_encontrada,
            etiquetas=lista_etiquetas,
        )
        # Desde SQLAlchemy 2.0 un objeto nuevo no entra a la sesión "por
        # arrastre" desde otro: hay que agregarlo explícitamente.
        db.session.add(pregunta)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise
    return pregunta