from rest_framework.permissions import BasePermission

from .models import Empleado


class TieneRolPermitido(BasePermission):
    """
    Permiso base para la API REST: solo deja pasar a superusuarios de Django
    o a Empleados activos cuyo cargo esté en `cargos_permitidos`.
    Replica la lógica del decorador requiere_rol usado en las vistas clásicas.
    """
    cargos_permitidos = ()

    @staticmethod
    def _cargo_del_empleado(request):
        """Busca el Empleado activo vinculado al usuario autenticado por email
        y devuelve el nombre de su cargo, o None si no existe o está inactivo."""
        try:
            empleado = Empleado.objects.select_related('id_cargo').get(
                email=request.user.email,
                estado='Activo'
            )
        except Empleado.DoesNotExist:
            return None
        return empleado.id_cargo.nombre

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        return self._cargo_del_empleado(request) in self.cargos_permitidos


class EsAdministrador(TieneRolPermitido):
    """Administradores y Gerentes (y superusers) pueden acceder."""
    cargos_permitidos = ('Administrador', 'Gerente')


class EsAdministradorOCajero(TieneRolPermitido):
    """Administradores, Gerentes y Cajeros (y superusers) pueden acceder."""
    cargos_permitidos = ('Administrador', 'Gerente', 'Cajero')


class EscrituraSoloRolPermitido(TieneRolPermitido):
    """
    Lectura abierta: cualquier usuario autenticado puede consultar
    (GET/HEAD/OPTIONS). Escribir (POST/PUT/PATCH/DELETE) requiere que el
    empleado activo tenga un cargo en `cargos_permitidos_escritura`.
    """
    cargos_permitidos_escritura = ()

    def has_permission(self, request, view):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        if request.user.is_superuser:
            return True
        return self._cargo_del_empleado(request) in self.cargos_permitidos_escritura


class EsAdministradorEscritura(EscrituraSoloRolPermitido):
    """Lectura abierta para cualquier autenticado; solo Administradores y
    Gerentes (y superusers) pueden crear, editar o eliminar."""
    cargos_permitidos_escritura = ('Administrador', 'Gerente')


class EsPersonalOperativoPedidos(TieneRolPermitido):
    """
    Restringe lectura Y escritura de Pedidos/DetallePedido al personal
    operativo del flujo de pedidos. A diferencia de EscrituraSoloRolPermitido,
    aquí ni siquiera la lectura es abierta: los pedidos no deben ser
    visibles para cualquier empleado.
    """
    cargos_permitidos = ('Mesero', 'Cocinero', 'Cajero', 'Administrador', 'Gerente')