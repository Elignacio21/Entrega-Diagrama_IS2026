# QA Platform

Plataforma colaborativa de preguntas y respuestas (Q&A) para estudiantes
universitarios. Trabajo Práctico Integrador — Ingeniería de Software 2026.

**Stack:** Python · Flask · SQLAlchemy · Alembic · pytest · Ruff · uv

## Puesta en marcha

Requisitos: [uv](https://docs.astral.sh/uv/) y Python 3.12+.

```bash
git clone <repositorio>
cd qa-platform
cp .env.example .env      # y ajustar valores si hace falta
uv sync                   # instala las dependencias exactas de uv.lock
uv run pytest             # tests
uv run ruff check .       # lint
uv run flask --app qa_platform run --debug
```

Verificar que funciona:

```bash
curl http://localhost:5000/health
# {"status":"ok"}
```

## Configuración

La configuración se lee de variables de entorno (ver `.env.example`).
**Nunca subir `.env` ni secretos reales a Git.**

| Variable       | Descripción                  | Por defecto          |
|----------------|------------------------------|----------------------|
| `SECRET_KEY`   | Clave secreta de Flask       | `development-only-key` |
| `DATABASE_URL` | URL de la base de datos      | `sqlite:///app.db`   |

En desarrollo se usa SQLite; en producción se puede usar PostgreSQL
cambiando solo `DATABASE_URL`.

## Migraciones (Alembic)

```bash
uv run alembic revision --autogenerate -m "descripcion del cambio"
# revisar el archivo generado en migrations/versions/
uv run alembic upgrade head      # aplicar
uv run alembic downgrade -1      # volver atrás
```

Las migraciones son parte del código y se versionan en Git.

## Estructura

```
src/qa_platform/
├── __init__.py       # Application factory: create_app()
├── config.py         # Configuración desde variables de entorno
├── extensions.py     # Instancia compartida de SQLAlchemy (db)
├── models/           # Modelos del dominio (según el diagrama UML)
├── api/              # Blueprints JSON (health, ...)
├── web/              # Blueprints HTML / Jinja2
├── services/         # Lógica de negocio (incl. estrategias LLM)
├── templates/
└── static/
migrations/           # Migraciones de Alembic
tests/                # pytest
```

## Flujo de trabajo

- Una rama por issue, con PR hacia `main`.
- Antes de abrir el PR: `uv run ruff check .` y `uv run pytest` deben pasar.
- `pyproject.toml` y `uv.lock` se versionan; `.venv/` no.
