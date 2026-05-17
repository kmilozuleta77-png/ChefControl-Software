from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# NUEVO: Importamos herramientas matemáticas de Django
from django.db.models import Sum, F

# Importamos las tablas de MySQL que el Dashboard necesita
from .models import Empleado, Pedido, Producto

# -------------------------------------------------------------------
# VISTA 1: LOGIN
# -------------------------------------------------------------------
def login_view(request):
    if request.method == 'POST':
        usu = request.POST.get('username')
        pas = request.POST.get('password')
        
        usuario_valido = authenticate(request, username=usu, password=pas)
        
        if usuario_valido is not None:
            login(request, usuario_valido)
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
            
    return render(request, 'login.html')

# -------------------------------------------------------------------
# VISTA 2: CERRAR SESIÓN
# -------------------------------------------------------------------
def logout_view(request):
    logout(request)
    return redirect('login')

# -------------------------------------------------------------------
# VISTA 3: DASHBOARD PRINCIPAL (Con datos 100% reales)
# -------------------------------------------------------------------
@login_required(login_url='login')
def dashboard_view(request):
    # 1. Total de empleados
    total_empleados = Empleado.objects.count()
    
    # 2. Total de pedidos
    total_pedidos = Pedido.objects.count()
    
    # 3. Ventas totales (Sumamos la columna 'total' de todos los pedidos)
    suma_ventas = Pedido.objects.aggregate(Sum('total'))['total__sum']
    ventas_dia = suma_ventas if suma_ventas is not None else 0
    
    # 4. Alertas de Inventario (Comparamos la columna stock vs stock_minimo)
    alertas_inventario = Producto.objects.filter(stock__lte=F('stock_minimo')).count()
    
    # 5. Últimos 5 Pedidos (select_related nos trae la info de la mesa y el empleado vinculados)
    pedidos_recientes = Pedido.objects.select_related('id_mesa', 'id_empleado').order_by('-fecha_pedido')[:5]
    
    # Empacamos los datos calculados en la caja (context)
    context = {
        'cantidad_empleados': total_empleados,
        'total_pedidos': total_pedidos,
        'ventas_dia': ventas_dia,
        'alertas_inventario': alertas_inventario,
        'pedidos_recientes': pedidos_recientes,
    }
    
    return render(request, 'index.html', context)

# -------------------------------------------------------------------
# VISTA 4: INVENTARIO (Ruta de Sofía)
# -------------------------------------------------------------------
@login_required(login_url='login')
def inventario_view(request):
    return render(request, 'inventario.html')