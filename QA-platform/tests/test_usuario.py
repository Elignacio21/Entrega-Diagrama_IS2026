import pytest
from sqlalchemy.exc import IntegrityError

from qa_platform.extensions import db
from qa_platform.models import Autor, RolUsuario, Usuario


def crear_usuario(correo="ada@example.com", **extra):
    return Usuario(correo=correo, password="hash-de-prueba", **extra)


def test_autor_declara_crearRespuesta_como_metodo_abstracto():
    assert hasattr(Autor, "crearRespuesta")


def test_usuario_hereda_de_autor():
    assert issubclass(Usuario, Autor)
    assert isinstance(crear_usuario(), Autor)


def test_usuario_tiene_los_atributos_del_diagrama():
    usuario = crear_usuario(rol=RolUsuario.ADMIN)

    assert hasattr(usuario, "identificacion")
    assert usuario.correo == "ada@example.com"
    assert usuario.password == "hash-de-prueba"
    assert usuario.rol == RolUsuario.ADMIN


def test_rol_usa_el_enum_y_tiene_valor_por_defecto(app):
    usuario = crear_usuario()
    db.session.add(usuario)
    db.session.commit()
    db.session.expire_all()

    guardado = db.session.get(Usuario, usuario.identificacion)
    assert guardado.rol is RolUsuario.USUARIO_GENERAL


def test_un_usuario_se_recupera_como_autor(app):
    usuario = crear_usuario()
    db.session.add(usuario)
    db.session.commit()
    db.session.expire_all()

    como_autor = db.session.get(Autor, usuario.identificacion)
    assert isinstance(como_autor, Usuario)


def test_el_correo_es_unico(app):
    db.session.add(crear_usuario())
    db.session.commit()

    db.session.add(crear_usuario())
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()