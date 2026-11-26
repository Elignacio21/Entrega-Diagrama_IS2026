from flask import Blueprint, request

from qa_platform.errors import ErrorValidacion
from qa_platform.services.catalogo_service import listar_categorias
from qa_platform.services.pregunta_service import crear_pregunta, listar_preguntas

preguntas_bp = Blueprint("preguntas", __name__, url_prefix="/api")


def _a_diccionario(pregunta) -> dict:
    return {
        "identificacion": pregunta.identificacion,
        "titulo": pregunta.titulo,
        "cuerpo": pregunta.cuerpo,
        "fecha": pregunta.fecha.isoformat(),
        "categoria": pregunta.categoria.nombre,
        "etiquetas": [etiqueta.nombre for etiqueta in pregunta.etiquetas],
        "autor_id": pregunta.autor.identificacion,
        "puntuacion": pregunta.calcularPuntuacion(),
    }


@preguntas_bp.post("/preguntas")
def registrar_pregunta():
    """Adaptador HTTP: traduce JSON <-> dominio. Las reglas viven en el modelo."""
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        datos = {}

    # La fecha no se lee del cliente: la fija el sistema al crear la pregunta.
    try:
        pregunta = crear_pregunta(
            autor_id=datos.get("autor_id"),
            titulo=datos.get("titulo"),
            cuerpo=datos.get("cuerpo"),
            categoria=datos.get("categoria"),
            etiquetas=datos.get("etiquetas"),
        )
    except ErrorValidacion as error:
        return {"errores": error.errores}, 400

    return _a_diccionario(pregunta), 201


@preguntas_bp.get("/preguntas")
def obtener_preguntas():
    preguntas = listar_preguntas()
    return {
        "total": len(preguntas),
        "preguntas": [_a_diccionario(pregunta) for pregunta in preguntas],
    }, 200


@preguntas_bp.get("/categorias")
def obtener_categorias():
    return {"categorias": [categoria.nombre for categoria in listar_categorias()]}, 200