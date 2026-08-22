from django.utils import timezone
from django.contrib.auth import logout
from django.shortcuts import redirect
from .models import Empleado


class SesionTimeoutMiddleware:
    """Cierra la sesión si el usuario configuró un timeout personal
    (Empleado.sesion_timeout_min) y superó ese tiempo sin actividad.
    Si el campo es NULL, el usuario no tiene esta protección activada
    y el middleware no hace nada — es una preferencia opt-in, nunca
    forzada por un administrador sobre otro usuario."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            empleado = Empleado.objects.filter(
                email=request.user.email, estado='Activo'
            ).only('sesion_timeout_min').first()

            if empleado and empleado.sesion_timeout_min:
                ahora = timezone.now().timestamp()
                ultima_actividad = request.session.get('ultima_actividad')

                if ultima_actividad and (ahora - ultima_actividad) > empleado.sesion_timeout_min * 60:
                    logout(request)
                    return redirect('login')

                request.session['ultima_actividad'] = ahora

        return self.get_response(request)
