from datetime import datetime, timedelta
import pytest

from qa_platform.errors import ErrorNoEncontrado, ErrorValidacion
from qa_platform.models.ia import IA
from qa_platform.models.llm import Gemini, LLM, ModeloLocal, OpenIA
from qa_platform.models.pregunta import Pregunta
from qa_platform.services.ia_service import (
    configurar_ia,
    evaluar_pregunta_para_ia,
    procesar_respuestas_automaticas,
    reiniciar_configuracion_ia,
)
from qa_platform.services.pregunta_service import crear_pregunta, limpiar_preguntas
from qa_platform.services.respuesta_service import crear_respuesta
from qa_platform.services.usuario_service import limpiar_usuarios, registrar_usuario


@pytest.fixture(autouse=True)
def limpiar_estado():
    limpiar_preguntas()
    limpiar_usuarios()
    reiniciar_configuracion_ia()
    configurar_ia(llm=ModeloLocal(), tiempo_espera=timedelta(hours=24))


def test_pregunta_con_etiqueta_ia_help_recibe_respuesta():
    estudiante = registrar_usuario("estudiante@uni.edu", "password123")
    pregunta = crear_pregunta(
        estudiante.identificacion,
        "Duda de recursión",
        "¿Cuándo conviene usar recursión de cola?",
        "Programacion",
        etiquetas=["#ia-help", "python"],
    )

    respuesta = evaluar_pregunta_para_ia(pregunta.identificacion)

    assert respuesta is not None
    assert isinstance(respuesta.autor, IA)
    assert respuesta in pregunta.respuestas


def test_pregunta_sin_respuestas_superado_tiempo_espera_recibe_respuesta():
    estudiante = registrar_usuario("estudiante@uni.edu", "password123")
    pregunta = crear_pregunta(
        estudiante.identificacion,
        "Normalización 3FN",
        "¿Cómo elimino dependencias transitivas?",
        "Bases de datos",
    )

    # Antes de cumplir el tiempo de espera no debe responder
    antes = pregunta.fecha + timedelta(hours=23)
    assert evaluar_pregunta_para_ia(pregunta.identificacion, ahora=antes) is None

    # Una vez superado el tiempo de espera debe responder
    despues = pregunta.fecha + timedelta(hours=25)
    respuesta = evaluar_pregunta_para_ia(pregunta.identificacion, ahora=despues)

    assert respuesta is not None
    assert isinstance(respuesta.autor, IA)


def test_pregunta_con_respuestas_y_sin_etiqueta_no_recibe_respuesta_automatica():
    estudiante = registrar_usuario("estudiante@uni.edu", "password123")
    companero = registrar_usuario("companero@uni.edu", "password123")
    pregunta = crear_pregunta(
        estudiante.identificacion,
        "Consulta de Redes",
        "¿Diferencia entre TCP y UDP?",
        "Redes",
    )
    crear_respuesta(pregunta.identificacion, companero.identificacion, "TCP es orientado a conexión.")

    futuro = pregunta.fecha + timedelta(hours=72)
    assert evaluar_pregunta_para_ia(pregunta.identificacion, ahora=futuro) is None
    assert len(pregunta.respuestas) == 1


def test_ia_no_responde_dos_veces_la_misma_pregunta():
    estudiante = registrar_usuario("estudiante@uni.edu", "password123")
    pregunta = crear_pregunta(
        estudiante.identificacion,
        "Consulta con etiqueta",
        "Necesito ayuda urgente.",
        "Algoritmos y estructuras de datos",
        etiquetas=["#ia-help"],
    )

    primera = evaluar_pregunta_para_ia(pregunta.identificacion)
    segunda = evaluar_pregunta_para_ia(pregunta.identificacion, ahora=pregunta.fecha + timedelta(hours=48))

    assert primera is not None
    assert segunda is None
    assert len(pregunta.respuestas) == 1


def test_tiempo_de_espera_es_configurable():
    estudiante = registrar_usuario("estudiante@uni.edu", "password123")
    configurar_ia(tiempo_espera=timedelta(hours=2))

    pregunta = crear_pregunta(
        estudiante.identificacion,
        "Duda rápida",
        "¿Qué es un deadlock?",
        "Sistemas operativos",
    )

    assert evaluar_pregunta_para_ia(pregunta.identificacion, ahora=pregunta.fecha + timedelta(hours=1)) is None
    respuesta = evaluar_pregunta_para_ia(pregunta.identificacion, ahora=pregunta.fecha + timedelta(hours=2))
    assert respuesta is not None


def test_funciona_con_cualquier_llm_configurado():
    class ProveedorCustom(LLM):
        def generarCuerpo(self, p: Pregunta) -> str:
            return f"[CustomLLM] Ayuda personalizada para {p.titulo}"

    estudiante = registrar_usuario("estudiante@uni.edu", "password123")
    p1 = crear_pregunta(estudiante.identificacion, "P1", "Cuerpo 1", "Otros", etiquetas=["#ia-help"])
    p2 = crear_pregunta(estudiante.identificacion, "P2", "Cuerpo 2", "Otros", etiquetas=["#ia-help"])
    p3 = crear_pregunta(estudiante.identificacion, "P3", "Cuerpo 3", "Otros", etiquetas=["#ia-help"])

    configurar_ia(llm=Gemini(api_key="key-test"))
    r1 = evaluar_pregunta_para_ia(p1.identificacion)
    assert "Gemini" in r1.cuerpo

    configurar_ia(llm=OpenIA(api_key="key-test"))
    r2 = evaluar_pregunta_para_ia(p2.identificacion)
    assert "OpenIA" in r2.cuerpo

    configurar_ia(llm=ProveedorCustom())
    r3 = evaluar_pregunta_para_ia(p3.identificacion)
    assert r3.cuerpo == "[CustomLLM] Ayuda personalizada para P3"


def test_procesar_respuestas_automaticas_en_lote_y_validaciones():
    estudiante = registrar_usuario("estudiante@uni.edu", "password123")
    p_etiqueta = crear_pregunta(estudiante.identificacion, "Con tag", "Cuerpo", "Otros", etiquetas=["#ia-help"])
    p_vencida = crear_pregunta(estudiante.identificacion, "Sin ayuda", "Cuerpo", "Otros")

    generadas = procesar_respuestas_automaticas(ahora=p_vencida.fecha + timedelta(hours=24))
    assert len(generadas) == 2

    with pytest.raises(ErrorNoEncontrado):
        evaluar_pregunta_para_ia(9999)

    with pytest.raises(ErrorValidacion):
        configurar_ia(tiempo_espera=timedelta(hours=-1))