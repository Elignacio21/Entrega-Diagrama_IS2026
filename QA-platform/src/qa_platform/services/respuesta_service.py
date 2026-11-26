from qa_platform.errors import ErrorNoEncontrado, ErrorValidacion
from qa_platform.models.respuesta import Respuesta
from qa_platform.services.pregunta_service import buscar_pregunta
from qa_platform.services.usuario_service import buscar_usuario


def _hay_texto(valor) -> bool:
    return isinstance(valor, str) and bool(valor.strip())


def listar_respuestas(pregunta_id) -> list[Respuesta]:
    """Respuestas de una pregunta. Lanza ErrorNoEncontrado si no existe."""
    pregunta = buscar_pregunta(pregunta_id)
    if pregunta is None:
        raise ErrorNoEncontrado({"pregunta": "La pregunta no existe"})
    return list(pregunta.respuestas)


def crear_respuesta(pregunta_id, autor_id, cuerpo) -> Respuesta:
    """Registra la respuesta de un usuario a una pregunta.

- pregunta_id: identificacion de una Pregunta existente.
- autor_id: identificacion de un Usuario registrado.
- cuerpo: texto de la respuesta.

    La fecha la fija el sistema y la respuesta nace sin aceptar. Las reglas
    de la respuesta viven en el modelo: acá solo se buscan la pregunta y el
    autor, y se delega en autor.crearRespuesta().

    Lanza ErrorNoEncontrado si la pregunta no existe, y ErrorValidacion con
    todos los errores encontrados si el autor o el cuerpo no son válidos.
    """
    pregunta = buscar_pregunta(pregunta_id)
    if pregunta is None:
        raise ErrorNoEncontrado({"pregunta": "La pregunta no existe"})

    errores: dict[str, str] = {}
    autor = buscar_usuario(autor_id)
    if autor is None:
        errores["autor"] = "El usuario no está registrado"
    if not _hay_texto(cuerpo):
        errores["cuerpo"] = "El cuerpo es obligatorio"
    if errores:
        raise ErrorValidacion(errores)

    respuesta = autor.crearRespuesta(pregunta, cuerpo)
    if getattr(respuesta, "identificacion", None) is None:
        respuesta.identificacion = len(pregunta.respuestas)
    return respuesta


def aceptar_respuesta(pregunta_id, respuesta_id, usuario_id) -> Respuesta:
    """Marca una respuesta de una pregunta como aceptada por el autor de esta."""
    pregunta = buscar_pregunta(pregunta_id)
    if pregunta is None:
        raise ErrorNoEncontrado({"pregunta": "La pregunta no existe"})

    respuesta = next(
        (r for r in pregunta.respuestas if getattr(r, "identificacion", None) == respuesta_id),
        None,
    )
    if respuesta is None:
        raise ErrorNoEncontrado({"respuesta": "La respuesta no existe"})

    usuario = buscar_usuario(usuario_id)
    if usuario is None:
        raise ErrorValidacion({"autor": "El usuario no está registrado"})

    usuario.aceptarRespuesta(respuesta)
    return respuesta