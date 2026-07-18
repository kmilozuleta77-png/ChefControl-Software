import json
import logging
from datetime import date, datetime, timedelta
from django.utils import timezone
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

# Mapeo de códigos frontend → valores exactos del ENUM metodo_pago en la BD
METODOS_PAGO_DB = {
    'efectivo':        'Efectivo',
    'tarjeta_debito':  'Tarjeta Débito',
    'tarjeta_credito': 'Tarjeta Crédito',
    'nequi':           'Transferencia',
}

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

def rango_dia(fecha):
    """Devuelve (inicio_aware, fin_aware) del día calendario dado en America/Bogota."""
    tz = timezone.get_current_timezone()
    inicio = timezone.make_aware(datetime.combine(fecha, datetime.min.time()), tz)
    return inicio, inicio + timedelta(days=1)


@login_required(login_url='login')
def dashboard_view(request):
    hoy = timezone.localdate()
    inicio_hoy, fin_hoy = rango_dia(hoy)
    inicio_ayer, fin_ayer = rango_dia(hoy - timedelta(days=1))

    empleados_activos = Empleado.objects.filter(estado='Activo').count()
    empleados_descanso = Empleado.objects.filter(estado='Descanso').count()
    total_pedidos = Pedido.objects.filter(
        fecha_pedido__gte=inicio_hoy, fecha_pedido__lt=fin_hoy
    ).count()

    suma_ventas = Factura.objects.filter(
        fecha_factura__gte=inicio_hoy, fecha_factura__lt=fin_hoy
    ).aggregate(Sum('total'))['total__sum']
    ventas_dia = suma_ventas if suma_ventas is not None else 0

    suma_ayer = Factura.objects.filter(
        fecha_factura__gte=inicio_ayer, fecha_factura__lt=fin_ayer
    ).aggregate(Sum('total'))['total__sum']
    ventas_ayer = suma_ayer if suma_ayer is not None else 0
    if ventas_ayer > 0:
        porcentaje_ventas = round(((ventas_dia - ventas_ayer) / ventas_ayer) * 100, 1)
    else:
        porcentaje_ventas = None

    alertas_inventario = Producto.objects.filter(stock__lte=F('stock_minimo')).count()
    alertas = Producto.objects.filter(stock__lte=F('stock_minimo')).select_related('id_categoria').order_by('stock')
    mesas_libres = Mesa.objects.filter(estado='Disponible').count()
    mesas_ocupadas = Mesa.objects.filter(estado='Ocupada').count()
    mesas_reservadas = Mesa.objects.filter(estado='Reservada').count()
    mesas_lista = Mesa.objects.all().order_by('numero_mesa')
    pedidos_en_cocina = Pedido.objects.filter(estado='En Preparación').count()

    # select_related completo: mesa, empleado y cliente evitan N+1 queries en el template
    pedidos_recientes = (
        Pedido.objects
        .select_related('id_mesa', 'id_empleado', 'id_cliente')
        .order_by('-fecha_pedido')[:10]
    )

    context = {
        'empleados_activos': empleados_activos,
        'empleados_descanso': empleados_descanso,
        'total_pedidos': total_pedidos,
        'ventas_dia': ventas_dia,
        'alertas_inventario': alertas_inventario,
        'alertas': alertas,
        'porcentaje_ventas': porcentaje_ventas,
        'mesas_libres': mesas_libres,
        'mesas_ocupadas': mesas_ocupadas,
        'mesas_reservadas': mesas_reservadas,
        'mesas_lista': mesas_lista,
        'pedidos_en_cocina': pedidos_en_cocina,
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
                    fecha_pedido=timezone.now(),
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
        .filter(estado__in=['Pendiente', 'En Preparación'])
        .prefetch_related('detallepedido_set__id_producto')
        .order_by('fecha_pedido')
    )
    return render(request, 'cocina.html', {'pedidos': pedidos_cocina})


# -----------------------------------------------------------------------
# MINI-API: POLLING DE PEDIDOS PENDIENTES PARA KDS (reemplaza location.reload)
# -----------------------------------------------------------------------

@login_required(login_url='login')
@requiere_rol('Cocinero', 'Administrador')
def api_pedidos_cocina(request):
    """Devuelve los pedidos pendientes en JSON para el polling del KDS."""
    pedidos_qs = (
        Pedido.objects
        .filter(estado__in=['Pendiente', 'En Preparación'])
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
            'estado': pedido.estado,
            'mesa': pedido.id_mesa.numero_mesa if pedido.id_mesa else '—',
            'observaciones': pedido.observaciones or '',
            'detalles': detalles,
        })

    return JsonResponse({'pedidos': pedidos_data})


# -----------------------------------------------------------------------
# MINI-API: INICIAR PREPARACIÓN DESDE COCINA
# -----------------------------------------------------------------------

@login_required(login_url='login')
@requiere_rol('Cocinero', 'Administrador')
def iniciar_preparacion_api(request, id_pedido):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'mensaje': 'Método no permitido.'}, status=405)
    try:
        pedido = Pedido.objects.get(id_pedido=id_pedido)
        if pedido.estado != 'Pendiente':
            return JsonResponse(
                {'status': 'error', 'mensaje': 'El pedido no está en estado Pendiente.'},
                status=400
            )
        pedido.estado = 'En Preparación'
        pedido.save()
        return JsonResponse({'status': 'success', 'mensaje': 'Preparación iniciada.'})
    except Pedido.DoesNotExist:
        return JsonResponse({'status': 'error', 'mensaje': 'Pedido no encontrado.'}, status=404)
    except Exception:
        logger.exception("Error al iniciar preparación del pedido #%s", id_pedido)
        return JsonResponse({'status': 'error', 'mensaje': 'Error interno.'}, status=500)


# -----------------------------------------------------------------------
# MINI-API: CAMBIAR ESTADO A LISTO DESDE COCINA
# -----------------------------------------------------------------------

@login_required(login_url='login')
@requiere_rol('Cocinero', 'Administrador')
def completar_pedido_api(request, id_pedido):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'mensaje': 'Método no permitido.'}, status=405)
    try:
        pedido = Pedido.objects.get(id_pedido=id_pedido)
        if pedido.estado != 'En Preparación':
            return JsonResponse(
                {'status': 'error', 'mensaje': 'El pedido debe iniciarse primero.'},
                status=400
            )
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
    """Cierra un pedido: lo marca Pagado y emite el registro Factura correspondiente."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'mensaje': 'Método no permitido.'}, status=405)
    try:
        data               = json.loads(request.body) if request.body else {}
        metodo_pago_codigo = data.get('metodo_pago', 'efectivo')
        if metodo_pago_codigo not in METODOS_PAGO_DB:
            logger.warning(
                "metodo_pago desconocido '%s' en pedido #%s; aplicando fallback 'Efectivo'",
                metodo_pago_codigo, id_pedido,
            )
        metodo_pago      = METODOS_PAGO_DB.get(metodo_pago_codigo, 'Efectivo')
        tipo_comprobante = data.get('tipo_comprobante', 'pos')

        pedido   = Pedido.objects.get(id_pedido=id_pedido)
        empleado = Empleado.objects.get(email=request.user.email, estado='Activo')

        # Guardia contra doble pago (id_pedido es OneToOne; un segundo create lanzaría IntegrityError)
        if pedido.estado == 'Pagado' or Factura.objects.filter(id_pedido=pedido).exists():
            return JsonResponse(
                {'status': 'error', 'mensaje': 'Este pedido ya fue facturado.'},
                status=400
            )

        # pedido.total ya incluye el INC 8% (Impuesto Nacional al Consumo para restaurantes)
        subtotal = (pedido.total / Decimal('1.08')).quantize(Decimal('0.01'))
        impuesto = (pedido.total - subtotal).quantize(Decimal('0.01'))
        # total = pedido.total → subtotal + impuesto cuadran exacto por construcción

        with transaction.atomic():
            Factura.objects.create(
                id_pedido    =pedido,
                id_empleado  =empleado,
                fecha_factura=timezone.now(),
                subtotal     =subtotal,
                impuesto     =impuesto,
                total        =pedido.total,
                metodo_pago  =metodo_pago,
                estado       ='Pagada',
                observaciones='Factura DIAN' if tipo_comprobante == 'fe' else 'Tiquete POS',
            )
            pedido.estado = 'Pagado'
            pedido.save()

        return JsonResponse({'status': 'success'})

    except Pedido.DoesNotExist:
        return JsonResponse({'status': 'error', 'mensaje': 'Pedido no encontrado.'}, status=404)
    except Empleado.DoesNotExist:
        return JsonResponse({'status': 'error', 'mensaje': 'Empleado no encontrado para este usuario.'}, status=404)
    except (InvalidOperation, ValueError) as e:
        logger.warning("Datos inválidos al pagar pedido #%s: %s", id_pedido, e)
        return JsonResponse({'status': 'error', 'mensaje': 'Datos de pago inválidos.'}, status=400)
    except Exception:
        logger.exception("Error al procesar pago del pedido #%s", id_pedido)
        return JsonResponse({'status': 'error', 'mensaje': 'Error interno.'}, status=500)