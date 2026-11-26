import pytest

from qa_platform import create_app
from qa_platform.config import Config
from qa_platform.extensions import db
from qa_platform.services.catalogo_service import sembrar_categorias


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


@pytest.fixture(autouse=True)
def app():
    """App + base de datos limpia para CADA test.

    Es autouse porque ahora casi todo (servicios, API) necesita una base: antes
    los datos vivían en listas globales y no hacía falta. Cada test arranca con
    las tablas vacías (salvo las categorías iniciales) y los ids reiniciados.
    """
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        sembrar_categorias()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()