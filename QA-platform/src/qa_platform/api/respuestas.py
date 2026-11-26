from qa_platform.services.voto_service import votar_respuesta


@respuestas_bp.post("/<int:respuesta_id>/votar")
def registrar_voto_respuesta(pregunta_id, respuesta_id):
    """Adaptador HTTP para votar una respuesta."""
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        datos = {}

    try:
        respuesta = votar_respuesta(
            pregunta_id=pregunta_id,
            respuesta_id=respuesta_id,
            usuario_id=datos.get("autor_id") or datos.get("usuario_id"),
            tipo=datos.get("tipo"),
        )
    except ErrorNoEncontrado as error:
        return {"errores": error.errores}, 404
    except ErrorValidacion as error:
        return {"errores": error.errores}, 400

    return _a_diccionario(respuesta), 200