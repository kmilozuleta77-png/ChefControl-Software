from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages # Para enviar mensajes de error a la pantalla
from django.contrib.auth import authenticate, login, logout

# Vista para la pantalla de Login
def login_view(request):
    # 1. Preguntamos si el navegador nos está enviando datos (POST)
    if request.method == 'POST':
        # 2. Capturamos lo que el usuario escribió en las cajas de texto (los 'name' que pusiste)
        usu = request.POST.get('username')
        pas = request.POST.get('password')
        
        # 3. Django verifica si esas credenciales existen en la base de datos
        usuario_valido = authenticate(request, username=usu, password=pas)
        
        if usuario_valido is not None:
            # 4. Si es correcto, iniciamos la sesión (crea la cookie)
            login(request, usuario_valido)
            # 5. Redirigimos directamente al dashboard
            return redirect('dashboard')
        else:
            # 6. Si es incorrecto, preparamos un mensaje de error
            messages.error(request, 'Usuario o contraseña incorrectos.')
            
    # Si no es POST (es decir, solo entró a la página a mirar), le mostramos el HTML vacío
    return render(request, 'login.html')

# Vista para el Dashboard principal
@login_required(login_url='login')  # Este es el guardia
def dashboard_view(request):
    return render(request, 'index.html')
def logout_view(request):
    logout(request) # Esto destruye la sesión
    return redirect('login') # Y lo manda de vuelta a la pantalla de inicio