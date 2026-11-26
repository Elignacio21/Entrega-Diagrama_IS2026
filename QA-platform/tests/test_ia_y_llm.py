import inspect
import pytest

from qa_platform.errors import ErrorValidacion
from qa_platform.models import ia as ia_module
from qa_platform.models import llm as llm_module
from qa_platform.models.autor import Autor
from qa_platform.models.categoria import Categoria
from qa_platform.models.enums import RolUsuario
from qa_platform.models.etiqueta import Etiqueta
from qa_platform.models.ia import IA
from qa_platform.models.llm import Gemini, LLM, ModeloLocal, OpenIA
from qa_platform.models.pregunta import Pregunta
from qa_platform.models.respuesta import Respuesta
from qa_platform.models.usuario import Usuario


def _crear_pregunta_ejemplo() -> Pregunta:
    estudiante = Usuario(
        identificacion=1,
        correo="estudiante@uni.edu",
        password="hash_seguro_password",
        rol=RolUsuario.USUARIO_GENERAL,
    )
    return Pregunta(
        titulo="¿Qué ventaja tiene el patrón Strategy?",
        cuerpo="Quiero desacoplar los proveedores de IA del dominio.",
        categoria=Categoria("Ingenieria de software"),
        autor=estudiante,
        etiquetas=[Etiqueta("patrones"), Etiqueta("python")],
    )


# --- Tests de la interfaz LLM y sus estrategias (Issue Strategy) ---

def test_proveedores_implementan_interfaz_llm():
    assert isinstance(Gemini(api_key="clave-prueba"), LLM)
    assert isinstance(OpenIA(api_key="clave-prueba"), LLM)
    assert isinstance(ModeloLocal(), LLM)


def test_generar_cuerpo_devuelve_string_en_cada_estrategia():
    pregunta = _crear_pregunta_ejemplo()
    for estrategia in (
        Gemini(api_key="clave-prueba"),
        OpenIA(api_key="clave-prueba"),
        ModeloLocal(),
    ):
        cuerpo = estrategia.generarCuerpo(pregunta)
        assert isinstance(cuerpo, str)
        assert len(cuerpo.strip()) > 0


def test_lectura_desde_variables_de_entorno_y_sin_claves_hardcodeadas(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "env-gemini-123")
    monkeypatch.setenv("OPENAI_API_KEY", "env-openai-456")

    assert Gemini().api_key == "env-gemini-123"
    assert OpenIA().api_key == "env-openai-456"

    codigo_llm = inspect.getsource(llm_module)
    assert "AIza" not in codigo_llm
    assert "sk-" not in codigo_llm


def test_falla_si_falta_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    pregunta = _crear_pregunta_ejemplo()

    with pytest.raises(ErrorValidacion):
        Gemini(api_key="").generarCuerpo(pregunta)

    with pytest.raises(ErrorValidacion):
        OpenIA(api_key="").generarCuerpo(pregunta)


# --- Tests de la clase IA (Issue Agente IA) ---

def test_ia_hereda_de_autor_y_tiene_atributo_modelo():
    gemini = Gemini(api_key="clave-prueba")
    ia = IA(modelo=gemini)

    assert isinstance(ia, Autor)
    assert ia.modelo is gemini


def test_set_llm_cambia_proveedor_en_tiempo_de_ejecucion():
    pregunta = _crear_pregunta_ejemplo()
    ia = IA()

    ia.setLLM(ModeloLocal())
    assert "ModeloLocal" in ia.generarCuerpoRespuesta(pregunta)

    ia.setLLM(OpenIA(api_key="clave-prueba"))
    assert "OpenIA" in ia.generarCuerpoRespuesta(pregunta)


def test_crear_respuesta_igual_que_usuario():
    pregunta = _crear_pregunta_ejemplo()
    ia = IA()
    ia.setLLM(Gemini(api_key="clave-prueba"))

    respuesta = ia.crearRespuesta(pregunta)
    assert isinstance(respuesta, Respuesta)
    assert respuesta.autor is ia
    assert respuesta.pregunta is pregunta
    assert respuesta in pregunta.respuestas
    assert "Gemini" in respuesta.cuerpo


def test_agregar_nuevo_proveedor_sin_modificar_clases_existentes():
    class AnthropicClaude(LLM):
        def generarCuerpo(self, p: Pregunta) -> str:
            return f"[Claude] Explicación sobre {p.titulo}"

    pregunta = _crear_pregunta_ejemplo()
    ia = IA()
    ia.setLLM(AnthropicClaude())
    respuesta = ia.crearRespuesta(pregunta)

    assert respuesta.cuerpo == "[Claude] Explicación sobre ¿Qué ventaja tiene el patrón Strategy?"


def test_ia_no_conoce_proveedores_concretos():
    codigo_ia = inspect.getsource(ia_module)
    assert "Gemini" not in codigo_ia
    assert "OpenIA" not in codigo_ia
    assert "ModeloLocal" not in codigo_ia


def test_validaciones_ia():
    pregunta = _crear_pregunta_ejemplo()
    ia = IA()

    with pytest.raises(ErrorValidacion):
        ia.generarCuerpoRespuesta(pregunta)

    with pytest.raises(ErrorValidacion):
        ia.setLLM("proveedor_invalido")  # type: ignore[arg-type]