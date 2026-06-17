import json
from django.http import JsonResponse
from django.db import transaction
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F

# Importamos las tablas de MySQL que el Dashboard necesita
from .models import Empleado, Pedido, Producto, Categoria, Detallepedido, Mesa, Cliente, Cargo, Factura

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
    from django.db.models import F

    # GUARDAR NUEVO PRODUCTO
    if request.method == 'POST':
        nombre      = request.POST.get('nombre_item')
        id_categoria = request.POST.get('cat_item')
        stock       = request.POST.get('stock_actual')
        stock_min   = request.POST.get('stock_min')
        precio      = request.POST.get('precio')

        if nombre and id_categoria and stock and stock_min and precio:
            unidad = request.POST.get('unidad', '')
            Producto.objects.create(
                nombre       = nombre,
                id_categoria = Categoria.objects.get(id_categoria=id_categoria),
                stock        = stock,
                stock_minimo = stock_min,
                precio       = precio,
                descripcion  = unidad,
                estado       = 'Disponible'
            )
            messages.success(request, f'Producto "{nombre}" agregado correctamente.')
        else:
            messages.error(request, 'Por favor completa todos los campos.')

        return redirect('inventario')

    # TRAER DATOS
    productos       = Producto.objects.select_related('id_categoria').all()
    total           = productos.count()
    criticos        = productos.filter(stock__lte=F('stock_minimo') / 2).count()
    bajos           = productos.filter(stock__gt=F('stock_minimo') / 2, stock__lte=F('stock_minimo')).count()
    normales        = productos.filter(stock__gt=F('stock_minimo')).count()
    criticos_lista  = productos.filter(stock__lte=F('stock_minimo'))
    categorias      = Categoria.objects.all()

    context = {
        'productos':      productos,
        'total':          total,
        'criticos':       criticos,
        'bajos':          bajos,
        'normales':       normales,
        'criticos_lista': criticos_lista,
        'categorias':     categorias,
    }
    return render(request, 'inventario.html', context)
# -------------------------------------------------------------------
# -------------------------------------------------------------------
# VISTA 5: PUNTO DE VENTA POS (Avanzado - API JSON)
# -------------------------------------------------------------------
@login_required(login_url='login')
def crear_pedido_view(request):
    # 1. SI RECIBIMOS DATOS DE JAVASCRIPT (GUARDAR PEDIDO)
    if request.method == 'POST':
        try:
            # Desempacamos el paquete JSON que nos envía JavaScript
            data = json.loads(request.body)
            
            # Extraemos los datos generales del pedido
            id_empleado_front = data['id_empleado']
            id_mesa_front = data['id_mesa']
            tipo_pedido_front = data['tipo_pedido']
            observaciones_front = data.get('observaciones', '')
            total_front = data['total']
            lista_productos = data['productos'] # Esto es una lista de los platos elegidos
            
            # Abrimos la bóveda de seguridad de la base de datos
            with transaction.atomic():
                # A. Buscamos los objetos reales en la base de datos
                empleado_obj = Empleado.objects.get(id_empleado=id_empleado_front)
                mesa_obj = Mesa.objects.get(id_mesa=id_mesa_front)
                
                # B. Guardamos el PADRE (La tabla Pedido)
                nuevo_pedido = Pedido.objects.create(
                    id_empleado=empleado_obj,
                    id_mesa=mesa_obj,
                    tipo_pedido=tipo_pedido_front,
                    observaciones=observaciones_front,
                    total=total_front,
                    estado='Pendiente' # El estado inicial para que la cocina lo vea
                )
                
                # C. Guardamos los HIJOS (La tabla Detallepedido)
                for item in lista_productos:
                    producto_obj = Producto.objects.get(id_producto=item['id'])
                    Detallepedido.objects.create(
                        id_pedido=nuevo_pedido, # Lo amarramos al pedido que acabamos de crear
                        id_producto=producto_obj,
                        cantidad=item['cantidad'],
                        precio_unitario=producto_obj.precio,
                        
                    )
            
            # Si todo salió perfecto, le respondemos a JavaScript con éxito
            return JsonResponse({'status': 'success', 'mensaje': 'Pedido guardado en Maestro-Detalle correctamente.'})
            
        except Exception as e:
            # Si algo explota (ej. falta un dato), le avisamos a JavaScript el error
            return JsonResponse({'status': 'error', 'mensaje': str(e)})

    # 2. SI ABRIMOS LA PÁGINA NORMALMENTE (GET)
    categorias_menu = Categoria.objects.all()
    productos_menu = Producto.objects.all()
    # Como ya no usamos forms.py, enviamos las listas manualmente al HTML
    empleados_activos = Empleado.objects.filter(id_cargo__nombre='Mesero')
    mesas_activas = Mesa.objects.all()
    
    context = {
        'categorias': categorias_menu,
        'productos': productos_menu,
        'empleados': empleados_activos,
        'mesas': mesas_activas
    }
    
    return render(request, 'crear_pedido.html', context)
# -------------------------------------------------------------------
# VISTA 6: PANTALLA DE COCINA (KDS - Kitchen Display System)
# -------------------------------------------------------------------
@login_required(login_url='login')
def cocina_view(request):
    # La cocina solo ve órdenes en estado 'Pendiente', las más antiguas primero
    pedidos_cocina = Pedido.objects.filter(estado='Pendiente').order_by('fecha_pedido')
    
    context = {
        'pedidos': pedidos_cocina
    }
    return render(request, 'cocina.html', context)


# -------------------------------------------------------------------
# MINI-API: CAMBIAR ESTADO A LISTO DESDE COCINA
# -------------------------------------------------------------------
@login_required(login_url='login')
def completar_pedido_api(request, id_pedido):
    if request.method == 'POST':
        try:
            # Buscamos el pedido en MySQL
            pedido = Pedido.objects.get(id_pedido=id_pedido)
            pedido.estado = 'Listo' # Cambiamos el estado
            pedido.save()
            return JsonResponse({'status': 'success', 'mensaje': 'Orden completada'})
        except Pedido.DoesNotExist:
            return JsonResponse({'status': 'error', 'mensaje': 'Pedido no encontrado'})
# -------------------------------------------------------------------
# VISTA 7: CAJA Y FACTURACIÓN
# -------------------------------------------------------------------
@login_required(login_url='login')
def facturacion_view(request):
    # El cajero solo ve los pedidos que ya salieron de la cocina ('Listo')
    pedidos_listos = Pedido.objects.filter(estado='Listo').order_by('fecha_pedido')
    return render(request, 'facturacion.html', {'pedidos': pedidos_listos})

# -------------------------------------------------------------------
# MINI-API: PROCESAR PAGO
# -------------------------------------------------------------------
@login_required(login_url='login')
def pagar_pedido_api(request, id_pedido):
    if request.method == 'POST':
        try:
            pedido = Pedido.objects.get(id_pedido=id_pedido)
            pedido.estado = 'Pagado' # Cerramos el ciclo de vida del pedido
            # NOTA PARA EL FUTURO: Aquí podríamos insertar el registro en la tabla Factura
            pedido.save()
            return JsonResponse({'status': 'success'})
        except Pedido.DoesNotExist:
            return JsonResponse({'status': 'error', 'mensaje': 'Pedido no encontrado'})
# -------------------------------------------------------------------
# VISTA 8: AJUSTAR STOCK
# -------------------------------------------------------------------
@login_required(login_url='login')
def ajustar_stock_view(request, id_producto):
    if request.method == 'POST':
        try:
            producto    = Producto.objects.get(id_producto=id_producto)
            tipo_mov    = request.POST.get('tipo_mov')
            cantidad    = int(request.POST.get('cant_mov', 0))

            if tipo_mov == 'entrada':
                producto.stock += cantidad
            elif tipo_mov == 'salida':
                producto.stock = max(0, producto.stock - cantidad)
            elif tipo_mov == 'ajuste':
                producto.stock = cantidad

            producto.save()
            messages.success(request, f'Stock de "{producto.nombre}" actualizado correctamente.')
        except Producto.DoesNotExist:
            messages.error(request, 'Producto no encontrado.')

    return redirect('inventario')            