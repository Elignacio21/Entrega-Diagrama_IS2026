from itertools import count

from qa_platform.errors import ErrorValidacion
from qa_platform.models.etiqueta import Etiqueta
from qa_platform.models.pregunta import Pregunta
from qa_platform.services.catalogo_service import buscar_categoria
from qa_platform.services.usuario_service import buscar_usuario

_preguntas_en_memoria: list[Pregunta] = []
_siguiente_id = count(start=1)


def listar_preguntas() -> list[Pregunta]:
    """Devuelve las preguntas guardadas en memoria."""
    return list(_preguntas_en_memoria)


def buscar_pregunta(pregunta_id) -> Pregunta | None:
    """Busca una pregunta por su identificacion; None si no existe."""
    # bool es un subtipo de int en Python: True == 1, y no debe valer como id.
    if isinstance(pregunta_id, bool) or not isinstance(pregunta_id, int):
        return None
    for pregunta in _preguntas_en_memoria:
        if pregunta.identificacion == pregunta_id:
            return pregunta
    return None


def limpiar_preguntas() -> None:
    """Limpia los datos en memoria y reinicia los identificadores."""
    global _siguiente_id
    _preguntas_en_memoria.clear()
    _siguiente_id = count(start=1)


def _convertir_etiquetas(nombres) -> tuple[list[Etiqueta], str | None]:
    """Convierte una lista de textos en Etiquetas (minúsculas, sin espacios).

    Devuelve (etiquetas, mensaje_de_error). Si no se envía nada, no hay
    etiquetas: son opcionales.
    """
    if nombres is None:
        return [], None

    es_lista_de_textos = isinstance(nombres, list) and all(
        isinstance(nombre, str) and nombre.strip() for nombre in nombres
    )
    if not es_lista_de_textos:
        return [], "Las etiquetas deben ser una lista de textos no vacíos"

    return [Etiqueta(nombre.strip().lower()) for nombre in nombres], None


def crear_pregunta(autor_id, titulo, cuerpo, categoria, etiquetas=None) -> Pregunta:
    """Valida los datos, crea la pregunta del usuario y la guarda en memoria.

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

    lista_etiquetas, error_etiquetas = _convertir_etiquetas(etiquetas)
    if error_etiquetas:
        errores["etiquetas"] = error_etiquetas

    if errores:
        raise ErrorValidacion(errores)

    pregunta = autor.generarPregunta(
        titulo,
        cuerpo,
        categoria=categoria_encontrada,
        etiquetas=lista_etiquetas,
    )
    # El id se asigna recién acá: una pregunta inválida no consume identificadores.
    pregunta.identificacion = next(_siguiente_id)
    _preguntas_en_memoria.append(pregunta)
    return pregunta