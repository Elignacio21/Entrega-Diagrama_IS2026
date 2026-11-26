from flask import Flask

from qa_platform.config import Config
from qa_platform.extensions import db


def create_app(config_class=Config):
    """Application factory.

    Permite crear distintas instancias de la app (development, testing,
    production) cambiando solo la configuración, sin tocar el código.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    # Importamos los modelos para que SQLAlchemy conozca el metadata
    # (lo necesitará Alembic para autogenerar migraciones).
    from qa_platform import models  # noqa: F401
    from qa_platform.api.health import health_bp
    from qa_platform.api.preguntas import preguntas_bp
    from qa_platform.api.respuestas import respuestas_bp
    from qa_platform.api.usuarios import usuarios_bp
    from qa_platform.web.paginas import web_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(preguntas_bp)
    app.register_blueprint(respuestas_bp)
    app.register_blueprint(web_bp)

    return app