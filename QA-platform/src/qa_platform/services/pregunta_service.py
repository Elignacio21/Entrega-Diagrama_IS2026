from qa_platform.errors import ErrorValidacion
from qa_platform.models.etiqueta import Etiqueta
from qa_platform.models.pregunta import Pregunta
from qa_platform.models.usuario import Usuario
from qa_platform.services.catalogo_service import buscar_categoria
from qa_platform.services.usuario_service import listar_usuarios

_preguntas_en_memoria: list[Pregunta] = []


def listar_preguntas() -> list[Pregunta]:
    """Devuelve las preguntas guardadas en memoria."""
    return list(_preguntas_en_memoria)


def limpiar_preguntas() -> None:
    """Limpia los datos en memoria."""
    _preguntas_en_memoria.clear()


def _buscar_autor(autor_id) -> Usuario | None:
    # bool es un subtipo de int en Python: True == 1, y no debe valer como id.
    if isinstance(autor_id, bool) or not isinstance(autor_id, int):
        return None
    for usuario in listar_usuarios():
        if usuario.identificacion == autor_id:
            return usuario
    return None


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

    La fecha de publicación la fija el sistema (el momento de la creación);
    el cliente no puede elegirla.

    Lanza ErrorValidacion con todos los errores encontrados.
    """
    errores = Pregunta.validar_textos(titulo, cuerpo)

    autor = _buscar_autor(autor_id)
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
    _preguntas_en_memoria.append(pregunta)
    return pregunta