import json
import logging
from decimal import Decimal, InvalidOperation

from django.http import JsonResponse
from django.db import transaction
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F
from functools import wraps

from .models import Empleado, Pedido, Producto, Categoria, Detallepedido, Mesa, Cliente, Cargo, Factura

logger = logging.getLogger('restaurante')

# -----------------------------------------------------------------------
# DECORADOR DE ROL — Verifica que el usuario tenga un Empleado activo con
# el cargo indicado. Redirige al dashboard si no cumple el requisito.
# -----------------------------------------------------------------------

def requiere_rol(*cargos_permitidos):
    """Restringe una vista a empleados con los cargos indicados."""
    def decorador(funcion):
        @wraps(funcion)
        def wrapper(request, *args, **kwargs):
            # Superusuarios de Django pasan siempre (para administración)
            if request.user.is_superuser:
                return funcion(request, *args, **kwargs)
            try:
                empleado = Empleado.objects.select_related('id_cargo').get(
                    email=request.user.email,
                    estado='Activo'
                )
                if empleado.id_cargo.nombre in cargos_permitidos:
                    return funcion(request, *args, **kwargs)
            except Empleado.DoesNotExist:
                pass
            messages.error(request, 'No tienes permisos para acceder a esta sección.')
            return redirect('dashboard')
        return wrapper
    return decorador


# -----------------------------------------------------------------------
# VISTA 1: LOGIN
# -----------------------------------------------------------------------

def login_view(request):
    if request.method == 'POST':
        usu = request.POST.get('username', '').strip()
        pas = request.POST.get('password', '')

        if not usu or not pas:
            messages.error(request, 'Ingresa usuario y contraseña.')
            return render(request, 'login.html')

        usuario_valido = authenticate(request, username=usu, password=pas)

        if usuario_valido is not None:
            login(request, usuario_valido)
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'login.html')


# -----------------------------------------------------------------------
# VISTA 2: CERRAR SESIÓN
# -----------------------------------------------------------------------

def logout_view(request):
    logout(request)
    return redirect('login')


# -----------------------------------------------------------------------
# VISTA 3: DASHBOARD PRINCIPAL
# -----------------------------------------------------------------------

@login_required(login_url='login')
def dashboard_view(request):
    total_empleados = Empleado.objects.count()
    total_pedidos = Pedido.objects.count()

    suma_ventas = Pedido.objects.aggregate(Sum('total'))['total__sum']
    ventas_dia = suma_ventas if suma_ventas is not None else 0

    alertas_inventario = Producto.objects.filter(stock__lte=F('stock_minimo')).count()

    # select_related completo: mesa, empleado y cliente evitan N+1 queries en el template
    pedidos_recientes = (
        Pedido.objects
        .select_related('id_mesa', 'id_empleado', 'id_cliente')
        .order_by('-fecha_pedido')[:5]
    )

    context = {
        'cantidad_empleados': total_empleados,
        'total_pedidos': total_pedidos,
        'ventas_dia': ventas_dia,
        'alertas_inventario': alertas_inventario,
        'pedidos_recientes': pedidos_recientes,
    }
    return render(request, 'index.html', context)


# -----------------------------------------------------------------------
# VISTA 4: INVENTARIO
# -----------------------------------------------------------------------

@login_required(login_url='login')
def inventario_view(request):
    return render(request, 'inventario.html')


# -----------------------------------------------------------------------
# VISTA 5: PUNTO DE VENTA POS
# -----------------------------------------------------------------------

@login_required(login_url='login')
@requiere_rol('Mesero', 'Administrador')
def crear_pedido_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({'status': 'error', 'mensaje': 'Formato de datos inválido.'}, status=400)

        # --- Validación de campos obligatorios ---
        id_empleado_front = data.get('id_empleado')
        id_mesa_front = data.get('id_mesa')
        tipo_pedido_front = data.get('tipo_pedido', '').strip()
        observaciones_front = data.get('observaciones', '').strip()
        total_front = data.get('total')
        lista_productos = data.get('productos', [])

        if not id_empleado_front or not id_mesa_front:
            return JsonResponse({'status': 'error', 'mensaje': 'Mesero y mesa son obligatorios.'}, status=400)

        if not lista_productos:
            return JsonResponse({'status': 'error', 'mensaje': 'El pedido no puede estar vacío.'}, status=400)

        if tipo_pedido_front not in ('En mesa', 'Para llevar'):
            return JsonResponse({'status': 'error', 'mensaje': 'Tipo de pedido no válido.'}, status=400)

        # --- Validación del total ---
        try:
            total_validado = Decimal(str(total_front))
            if total_validado <= 0:
                raise ValueError
        except (InvalidOperation, ValueError, TypeError):
            return JsonResponse({'status': 'error', 'mensaje': 'Total inválido.'}, status=400)

        try:
            with transaction.atomic():
                # Validamos existencia de empleado y mesa antes de crear
                try:
                    empleado_obj = Empleado.objects.get(id_empleado=id_empleado_front)
                except Empleado.DoesNotExist:
                    return JsonResponse({'status': 'error', 'mensaje': 'Mesero no encontrado.'}, status=400)

                try:
                    mesa_obj = Mesa.objects.get(id_mesa=id_mesa_front)
                except Mesa.DoesNotExist:
                    return JsonResponse({'status': 'error', 'mensaje': 'Mesa no encontrada.'}, status=400)

                nuevo_pedido = Pedido.objects.create(
                    id_empleado=empleado_obj,
                    id_mesa=mesa_obj,
                    tipo_pedido=tipo_pedido_front,
                    observaciones=observaciones_front,
                    total=total_validado,
                    estado='Pendiente',
                )

                for item in lista_productos:
                    id_prod = item.get('id')
                    cantidad = item.get('cantidad', 0)

                    if not id_prod or int(cantidad) <= 0:
                        raise ValueError(f"Producto inválido en el carrito: {item}")

                    try:
                        producto_obj = Producto.objects.get(id_producto=id_prod)
                    except Producto.DoesNotExist:
                        raise ValueError(f"Producto #{id_prod} no existe en el menú.")

                    Detallepedido.objects.create(
                        id_pedido=nuevo_pedido,
                        id_producto=producto_obj,
                        cantidad=int(cantidad),
                        precio_unitario=producto_obj.precio,
                    )

            return JsonResponse({'status': 'success', 'mensaje': 'Pedido enviado a cocina.'})

        except ValueError as e:
            # Error de validación de negocio — mensaje seguro para el cliente
            logger.warning("Pedido rechazado por validación: %s", e)
            return JsonResponse({'status': 'error', 'mensaje': str(e)}, status=400)
        except Exception:
            # Error inesperado — log detallado interno, mensaje genérico al cliente
            logger.exception("Error inesperado al guardar pedido")
            return JsonResponse({'status': 'error', 'mensaje': 'Error interno. Intenta nuevamente.'}, status=500)

    # GET — Carga inicial del POS
    context = {
        'categorias': Categoria.objects.all(),
        'productos': Producto.objects.filter(estado='Disponible').select_related('id_categoria'),
        'empleados': Empleado.objects.filter(id_cargo__nombre='Mesero', estado='Activo'),
        'mesas': Mesa.objects.all(),
    }
    return render(request, 'crear_pedido.html', context)


# -----------------------------------------------------------------------
# VISTA 6: PANTALLA DE COCINA (KDS)
# -----------------------------------------------------------------------

@login_required(login_url='login')
@requiere_rol('Cocinero', 'Administrador')
def cocina_view(request):
    pedidos_cocina = (
        Pedido.objects
        .filter(estado='Pendiente')
        .prefetch_related('detallepedido_set__id_producto')
        .order_by('fecha_pedido')
    )
    return render(request, 'cocina.html', {'pedidos': pedidos_cocina})


# -----------------------------------------------------------------------
# MINI-API: POLLING DE PEDIDOS PENDIENTES PARA KDS (reemplaza location.reload)
# -----------------------------------------------------------------------

@login_required(login_url='login')
def api_pedidos_cocina(request):
    """Devuelve los pedidos pendientes en JSON para el polling del KDS."""
    pedidos_qs = (
        Pedido.objects
        .filter(estado='Pendiente')
        .prefetch_related('detallepedido_set__id_producto')
        .select_related('id_mesa')
        .order_by('fecha_pedido')
    )

    pedidos_data = []
    for pedido in pedidos_qs:
        detalles = [
            {
                'cantidad': d.cantidad,
                'producto': d.id_producto.nombre,
            }
            for d in pedido.detallepedido_set.all()
        ]
        pedidos_data.append({
            'id': pedido.id_pedido,
            'mesa': pedido.id_mesa.numero_mesa if pedido.id_mesa else '—',
            'observaciones': pedido.observaciones or '',
            'detalles': detalles,
        })

    return JsonResponse({'pedidos': pedidos_data})


# -----------------------------------------------------------------------
# MINI-API: CAMBIAR ESTADO A LISTO DESDE COCINA
# -----------------------------------------------------------------------

@login_required(login_url='login')
def completar_pedido_api(request, id_pedido):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'mensaje': 'Método no permitido.'}, status=405)
    try:
        pedido = Pedido.objects.get(id_pedido=id_pedido)
        pedido.estado = 'Listo'
        pedido.save()
        return JsonResponse({'status': 'success', 'mensaje': 'Orden completada.'})
    except Pedido.DoesNotExist:
        return JsonResponse({'status': 'error', 'mensaje': 'Pedido no encontrado.'}, status=404)
    except Exception:
        logger.exception("Error al completar pedido #%s", id_pedido)
        return JsonResponse({'status': 'error', 'mensaje': 'Error interno.'}, status=500)


# -----------------------------------------------------------------------
# VISTA 7: CAJA Y FACTURACIÓN
# -----------------------------------------------------------------------

@login_required(login_url='login')
@requiere_rol('Cajero', 'Administrador')
def facturacion_view(request):
    pedidos_listos = (
        Pedido.objects
        .filter(estado='Listo')
        .select_related('id_mesa', 'id_empleado')
        .order_by('fecha_pedido')
    )
    return render(request, 'facturacion.html', {'pedidos': pedidos_listos})


# -----------------------------------------------------------------------
# MINI-API: PROCESAR PAGO
# -----------------------------------------------------------------------

@login_required(login_url='login')
def pagar_pedido_api(request, id_pedido):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'mensaje': 'Método no permitido.'}, status=405)
    try:
        pedido = Pedido.objects.get(id_pedido=id_pedido)
        pedido.estado = 'Pagado'
        pedido.save()
        return JsonResponse({'status': 'success'})
    except Pedido.DoesNotExist:
        return JsonResponse({'status': 'error', 'mensaje': 'Pedido no encontrado.'}, status=404)
    except Exception:
        logger.exception("Error al procesar pago del pedido #%s", id_pedido)
        return JsonResponse({'status': 'error', 'mensaje': 'Error interno.'}, status=500)