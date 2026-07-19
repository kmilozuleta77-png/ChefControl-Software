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
from django.db.models import Sum, F, Count, Q
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

    # TRAER DATOS (se excluyen los productos desactivados vía soft-delete)
    productos       = Producto.objects.select_related('id_categoria').exclude(estado='No Disponible')
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

# -------------------------------------------------------------------
# VISTA 8: AJUSTAR STOCK
# -------------------------------------------------------------------
@login_required(login_url='login')
def ajustar_stock_view(request, id_producto):
    if request.method == 'POST':
        try:
            producto = Producto.objects.get(id_producto=id_producto)
        except Producto.DoesNotExist:
            messages.error(request, 'Producto no encontrado.')
            return redirect('inventario')

        tipo_mov = request.POST.get('tipo_mov')

        # Validación numérica explícita: cant_mov puede llegar vacío o no numérico
        # si el POST se fuerza fuera del form (el <input type="number"> del HTML no lo garantiza).
        try:
            cantidad = int(request.POST.get('cant_mov', ''))
        except (ValueError, TypeError):
            messages.error(request, 'La cantidad debe ser un número entero.')
            return redirect('inventario')

        if cantidad <= 0:
            messages.error(request, 'La cantidad debe ser mayor que cero.')
            return redirect('inventario')

        if tipo_mov == 'entrada':
            producto.stock = (producto.stock or 0) + cantidad
        elif tipo_mov == 'salida':
            producto.stock = max(0, (producto.stock or 0) - cantidad)
        elif tipo_mov == 'ajuste':
            producto.stock = cantidad
        else:
            messages.error(request, 'Tipo de movimiento no válido.')
            return redirect('inventario')

        producto.save()
        messages.success(
            request,
            f'Stock de "{producto.nombre}" actualizado correctamente.'
        )

    return redirect('inventario')


# -------------------------------------------------------------------
# VISTA 9: ELIMINAR (DESACTIVAR) PRODUCTO
# -------------------------------------------------------------------
@login_required(login_url='login')
def eliminar_producto_view(request, id_producto):
    """Soft-delete: marca el producto como 'No Disponible' en vez de borrarlo físicamente.

    Detallepedido.id_producto usa PROTECT (ver models.py) para preservar el historial
    de ventas, así que un DELETE físico fallaría con ProtectedError en cualquier
    producto que ya se haya vendido. El ENUM real de estado en MySQL es
    ('Disponible', 'No Disponible', 'Agotado') — 'Inactivo' no es un valor válido
    y trunca el campo. 'No Disponible' oculta el producto de inventario y del POS
    (que ya filtra por estado='Disponible') sin tocar ese historial.
    """
    if request.method == 'POST':
        try:
            producto = Producto.objects.get(id_producto=id_producto)
            producto.estado = 'No Disponible'
            producto.save()
            messages.success(
                request,
                f'Producto "{producto.nombre}" eliminado del inventario.'
            )
        except Producto.DoesNotExist:
            messages.error(request, 'Producto no encontrado.')

    return redirect('inventario')


# -------------------------------------------------------------------
# VISTA 10: CLIENTES (listar + crear)
# -------------------------------------------------------------------
@login_required(login_url='login')
def clientes_view(request):

    # GUARDAR NUEVO CLIENTE
    if request.method == 'POST':
        nombres   = request.POST.get('nombres', '').strip()
        apellidos = request.POST.get('apellidos', '').strip()
        cedula    = request.POST.get('cedula', '').strip()
        telefono  = request.POST.get('telefono', '').strip()
        email     = request.POST.get('email', '').strip()
        direccion = request.POST.get('direccion', '').strip()

        if not nombres or not apellidos:
            messages.error(request, 'Nombres y apellidos son obligatorios.')
            return redirect('clientes')

        if cedula and Cliente.objects.filter(cedula=cedula).exists():
            messages.error(request, f'Ya existe un cliente con la cédula "{cedula}".')
            return redirect('clientes')

        if email and Cliente.objects.filter(email=email).exists():
            messages.error(request, f'Ya existe un cliente con el email "{email}".')
            return redirect('clientes')

        Cliente.objects.create(
            nombres        = nombres,
            apellidos      = apellidos,
            cedula         = cedula or None,
            telefono       = telefono or None,
            email          = email or None,
            direccion      = direccion or None,
            estado         = 'Activo',
            fecha_creacion = timezone.now(),
        )
        messages.success(request, f'Cliente "{nombres} {apellidos}" registrado correctamente.')
        return redirect('clientes')

    # TRAER DATOS (se excluyen los clientes desactivados vía soft-delete)
    busqueda = request.GET.get('q', '').strip()

    clientes = (
        Cliente.objects
        .exclude(estado='Inactivo')
        .annotate(visitas=Count('pedido'))
        .order_by('nombres', 'apellidos')
    )

    if busqueda:
        clientes = clientes.filter(
            Q(nombres__icontains=busqueda) |
            Q(apellidos__icontains=busqueda) |
            Q(cedula__icontains=busqueda) |
            Q(email__icontains=busqueda)
        )

    inicio_mes = timezone.localdate().replace(day=1)
    clientes_no_inactivos = Cliente.objects.exclude(estado='Inactivo')

    context = {
        'clientes':   clientes,
        'total':      clientes_no_inactivos.count(),
        'activos':    Cliente.objects.filter(estado='Activo').count(),
        'nuevos_mes': clientes_no_inactivos.filter(fecha_creacion__date__gte=inicio_mes).count(),
        'busqueda':   busqueda,
    }
    return render(request, 'clientes.html', context)


# -------------------------------------------------------------------
# VISTA 11: EDITAR CLIENTE
# -------------------------------------------------------------------
@login_required(login_url='login')
def editar_cliente_view(request, id_cliente):
    if request.method == 'POST':
        try:
            cliente = Cliente.objects.get(id_cliente=id_cliente)
        except Cliente.DoesNotExist:
            messages.error(request, 'Cliente no encontrado.')
            return redirect('clientes')

        nombres   = request.POST.get('nombres', '').strip()
        apellidos = request.POST.get('apellidos', '').strip()
        cedula    = request.POST.get('cedula', '').strip()
        telefono  = request.POST.get('telefono', '').strip()
        email     = request.POST.get('email', '').strip()
        direccion = request.POST.get('direccion', '').strip()

        if not nombres or not apellidos:
            messages.error(request, 'Nombres y apellidos son obligatorios.')
            return redirect('clientes')

        if cedula and Cliente.objects.filter(cedula=cedula).exclude(id_cliente=id_cliente).exists():
            messages.error(request, f'Ya existe otro cliente con la cédula "{cedula}".')
            return redirect('clientes')

        if email and Cliente.objects.filter(email=email).exclude(id_cliente=id_cliente).exists():
            messages.error(request, f'Ya existe otro cliente con el email "{email}".')
            return redirect('clientes')

        cliente.nombres   = nombres
        cliente.apellidos = apellidos
        cliente.cedula    = cedula or None
        cliente.telefono  = telefono or None
        cliente.email     = email or None
        cliente.direccion = direccion or None
        cliente.save()

        messages.success(request, f'Cliente "{nombres} {apellidos}" actualizado correctamente.')

    return redirect('clientes')


# -------------------------------------------------------------------
# VISTA 12: ELIMINAR (DESACTIVAR) CLIENTE
# -------------------------------------------------------------------
@login_required(login_url='login')
def eliminar_cliente_view(request, id_cliente):
    """Soft-delete: marca el cliente como 'Inactivo' en vez de borrarlo físicamente.

    fk_pedido_cliente tiene ON DELETE SET NULL (no PROTECT como en Producto), así
    que un DELETE físico no fallaría — pero dejaría los pedidos históricos de este
    cliente sin dueño, perdiendo esa trazabilidad en reportes. El soft-delete
    reutiliza el ENUM real de estado en MySQL: ('Activo', 'Inactivo').
    """
    if request.method == 'POST':
        try:
            cliente = Cliente.objects.get(id_cliente=id_cliente)
            cliente.estado = 'Inactivo'
            cliente.save()
            messages.success(
                request,
                f'Cliente "{cliente.nombres} {cliente.apellidos}" eliminado correctamente.'
            )
        except Cliente.DoesNotExist:
            messages.error(request, 'Cliente no encontrado.')

    return redirect('clientes')


# -------------------------------------------------------------------
# VISTA 13: PERSONAL / EMPLEADOS (listar + crear)
# -------------------------------------------------------------------
@login_required(login_url='login')
def personal_view(request):

    # GUARDAR NUEVO EMPLEADO
    if request.method == 'POST':
        nombres       = request.POST.get('nombres', '').strip()
        apellidos     = request.POST.get('apellidos', '').strip()
        cedula        = request.POST.get('cedula', '').strip()
        telefono      = request.POST.get('telefono', '').strip()
        email         = request.POST.get('email', '').strip()
        direccion     = request.POST.get('direccion', '').strip()
        fecha_ingreso = request.POST.get('fecha_ingreso', '').strip()
        id_cargo      = request.POST.get('id_cargo', '').strip()

        # nombres, apellidos, cedula, fecha_ingreso e id_cargo son NOT NULL en la BD
        if not nombres or not apellidos or not cedula or not fecha_ingreso or not id_cargo:
            messages.error(request, 'Nombres, apellidos, cédula, cargo y fecha de ingreso son obligatorios.')
            return redirect('personal')

        try:
            cargo = Cargo.objects.get(id_cargo=id_cargo)
        except Cargo.DoesNotExist:
            messages.error(request, 'El cargo seleccionado no existe.')
            return redirect('personal')

        if Empleado.objects.filter(cedula=cedula).exists():
            messages.error(request, f'Ya existe un empleado con la cédula "{cedula}".')
            return redirect('personal')

        if email and Empleado.objects.filter(email=email).exists():
            messages.error(request, f'Ya existe un empleado con el email "{email}".')
            return redirect('personal')

        Empleado.objects.create(
            id_cargo       = cargo,
            nombres        = nombres,
            apellidos      = apellidos,
            cedula         = cedula,
            telefono       = telefono or None,
            email          = email or None,
            direccion      = direccion or None,
            fecha_ingreso  = fecha_ingreso,
            estado         = 'Activo',
            fecha_creacion = timezone.now(),
        )
        messages.success(request, f'Empleado "{nombres} {apellidos}" registrado correctamente.')
        return redirect('personal')

    # TRAER DATOS (se excluyen los empleados desactivados vía soft-delete)
    busqueda = request.GET.get('q', '').strip()

    empleados = (
        Empleado.objects
        .exclude(estado='Inactivo')
        .select_related('id_cargo')
        .annotate(pedidos_atendidos=Count('pedido'))
        .order_by('nombres', 'apellidos')
    )

    if busqueda:
        empleados = empleados.filter(
            Q(nombres__icontains=busqueda) |
            Q(apellidos__icontains=busqueda) |
            Q(cedula__icontains=busqueda) |
            Q(email__icontains=busqueda)
        )

    inicio_mes = timezone.localdate().replace(day=1)
    empleados_no_inactivos = Empleado.objects.exclude(estado='Inactivo')

    context = {
        'empleados':  empleados,
        'cargos':     Cargo.objects.all().order_by('nombre'),
        'total':      empleados_no_inactivos.count(),
        'activos':    Empleado.objects.filter(estado='Activo').count(),
        'nuevos_mes': empleados_no_inactivos.filter(fecha_creacion__date__gte=inicio_mes).count(),
        'busqueda':   busqueda,
    }
    return render(request, 'personal.html', context)


# -------------------------------------------------------------------
# VISTA 14: EDITAR EMPLEADO
# -------------------------------------------------------------------
@login_required(login_url='login')
def editar_empleado_view(request, id_empleado):
    if request.method == 'POST':
        try:
            empleado = Empleado.objects.get(id_empleado=id_empleado)
        except Empleado.DoesNotExist:
            messages.error(request, 'Empleado no encontrado.')
            return redirect('personal')

        nombres       = request.POST.get('nombres', '').strip()
        apellidos     = request.POST.get('apellidos', '').strip()
        cedula        = request.POST.get('cedula', '').strip()
        telefono      = request.POST.get('telefono', '').strip()
        email         = request.POST.get('email', '').strip()
        direccion     = request.POST.get('direccion', '').strip()
        fecha_ingreso = request.POST.get('fecha_ingreso', '').strip()
        id_cargo      = request.POST.get('id_cargo', '').strip()

        if not nombres or not apellidos or not cedula or not fecha_ingreso or not id_cargo:
            messages.error(request, 'Nombres, apellidos, cédula, cargo y fecha de ingreso son obligatorios.')
            return redirect('personal')

        try:
            cargo = Cargo.objects.get(id_cargo=id_cargo)
        except Cargo.DoesNotExist:
            messages.error(request, 'El cargo seleccionado no existe.')
            return redirect('personal')

        if Empleado.objects.filter(cedula=cedula).exclude(id_empleado=id_empleado).exists():
            messages.error(request, f'Ya existe otro empleado con la cédula "{cedula}".')
            return redirect('personal')

        if email and Empleado.objects.filter(email=email).exclude(id_empleado=id_empleado).exists():
            messages.error(request, f'Ya existe otro empleado con el email "{email}".')
            return redirect('personal')

        empleado.id_cargo      = cargo
        empleado.nombres       = nombres
        empleado.apellidos     = apellidos
        empleado.cedula        = cedula
        empleado.telefono      = telefono or None
        empleado.email         = email or None
        empleado.direccion     = direccion or None
        empleado.fecha_ingreso = fecha_ingreso
        empleado.save()

        messages.success(request, f'Empleado "{nombres} {apellidos}" actualizado correctamente.')

    return redirect('personal')


# -------------------------------------------------------------------
# VISTA 15: ELIMINAR (DESACTIVAR) EMPLEADO
# -------------------------------------------------------------------
@login_required(login_url='login')
def eliminar_empleado_view(request, id_empleado):
    """Soft-delete: marca el empleado como 'Inactivo' en vez de borrarlo físicamente.

    A diferencia de Cliente (fk_pedido_cliente con ON DELETE SET NULL), aquí
    fk_pedido_empleado y fk_factura_empleado tienen ON DELETE RESTRICT: un
    DELETE físico de un empleado con historial de pedidos o facturas fallaría
    con IntegrityError. El soft-delete evita ese error y preserva la
    trazabilidad, reutilizando el ENUM real de estado en MySQL: ('Activo', 'Inactivo').
    """
    if request.method == 'POST':
        try:
            empleado = Empleado.objects.get(id_empleado=id_empleado)
            empleado.estado = 'Inactivo'
            empleado.save()
            messages.success(
                request,
                f'Empleado "{empleado.nombres} {empleado.apellidos}" eliminado correctamente.'
            )
        except Empleado.DoesNotExist:
            messages.error(request, 'Empleado no encontrado.')

    return redirect('personal')
