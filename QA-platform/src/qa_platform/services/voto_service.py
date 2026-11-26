from qa_platform.errors import ErrorNoEncontrado, ErrorValidacion
from qa_platform.models.enums import TipoVoto
from qa_platform.models.publicacion import Publicacion
from qa_platform.services.pregunta_service import buscar_pregunta
from qa_platform.services.usuario_service import buscar_usuario


def _resolver_tipo_voto(tipo) -> TipoVoto:
    if isinstance(tipo, TipoVoto):
        return tipo
    if isinstance(tipo, str):
        normalizado = tipo.strip().upper()
        if normalizado in TipoVoto.__members__:
            return TipoVoto[normalizado]
    raise ErrorValidacion(
        {"tipo": "El tipo de voto debe ser 'POSITIVO' o 'NEGATIVO'"}
    )


def _buscar_respuesta_en_pregunta(pregunta, respuesta_id):
    if pregunta is None:
        return None
    return next(
        (
            r
            for r in pregunta.respuestas
            if getattr(r, "identificacion", None) == respuesta_id
        ),
        None,
    )


def _emitir_voto(publicacion: Publicacion, usuario_id, tipo):
    if usuario_id is None:
        raise ErrorValidacion({"autor_id": "El autor_id es obligatorio"})

    usuario = buscar_usuario(usuario_id)
    if usuario is None:
        raise ErrorValidacion({"autor_id": "El usuario no está registrado"})

    tipo_voto = _resolver_tipo_voto(tipo)
    return usuario.votar(publicacion, tipo_voto)


def votar_pregunta(pregunta_id, usuario_id, tipo):
    """Vota una pregunta existente como POSITIVO o NEGATIVO."""
    pregunta = buscar_pregunta(pregunta_id)
    if pregunta is None:
        raise ErrorNoEncontrado({"pregunta": "La pregunta no existe"})

    _emitir_voto(pregunta, usuario_id, tipo)
    return pregunta


def votar_respuesta(pregunta_id, respuesta_id, usuario_id, tipo):
    """Vota una respuesta de una pregunta existente como POSITIVO o NEGATIVO."""
    pregunta = buscar_pregunta(pregunta_id)
    if pregunta is None:
        raise ErrorNoEncontrado({"pregunta": "La pregunta no existe"})

    respuesta = _buscar_respuesta_en_pregunta(pregunta, respuesta_id)
    if respuesta is None:
        raise ErrorNoEncontrado({"respuesta": "La respuesta no existe"})

    _emitir_voto(respuesta, usuario_id, tipo)
    return respuesta