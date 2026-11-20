from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

# Alembic obtiene la URL y el metadata desde la propia aplicación,
# para que exista una sola fuente de verdad (config.py / DATABASE_URL).
from qa_platform import create_app
from qa_platform.extensions import db

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

app = create_app()
DATABASE_URL = app.config["SQLALCHEMY_DATABASE_URI"]

# create_app() importa qa_platform.models, así que db.metadata ya conoce
# todas las tablas. Es lo que usa --autogenerate para comparar.
target_metadata = db.metadata


def run_migrations_offline() -> None:
    """Genera el SQL sin conectarse a la base."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Aplica las migraciones conectándose a la base."""
    connectable = create_engine(DATABASE_URL, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # Necesario para que SQLite pueda alterar tablas (dev vs prod parity)
            render_as_batch=connection.dialect.name == "sqlite",
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
