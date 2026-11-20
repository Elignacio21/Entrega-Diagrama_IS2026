from qa_platform.models import RolUsuario, TipoVoto


def test_rol_usuario_tiene_exactamente_admin_y_usuario_general():
    assert {rol.name for rol in RolUsuario} == {"ADMIN", "USUARIO_GENERAL"}


def test_tipo_voto_tiene_exactamente_positivo_y_negativo():
    assert {tipo.name for tipo in TipoVoto} == {"POSITIVO", "NEGATIVO"}


def test_los_valores_coinciden_con_los_nombres():
    assert all(rol.value == rol.name for rol in RolUsuario)
    assert all(tipo.value == tipo.name for tipo in TipoVoto)


def test_se_pueden_importar_desde_su_modulo():
    from qa_platform.models.enums import RolUsuario as Rol
    from qa_platform.models.enums import TipoVoto as Tipo

    assert Rol is RolUsuario
    assert Tipo is TipoVoto