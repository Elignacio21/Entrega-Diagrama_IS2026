from flask import Blueprint, render_template

web_bp = Blueprint("web", __name__)


@web_bp.get("/")
def inicio():
    """Página de prueba para registrar usuarios."""
    return render_template("registro.html")