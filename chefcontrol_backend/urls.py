from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from restaurante import views
from restaurante.api_views import (
    CargoViewSet,
    CategoriaViewSet,
    ClienteViewSet,
    EmpleadoViewSet,
    ProductoViewSet,
    MesaViewSet,
    PedidoViewSet,
    DetallePedidoViewSet,
    FacturaViewSet,
)

router = DefaultRouter()

router.register(r'cargos', CargoViewSet)
router.register(r'categorias', CategoriaViewSet)
router.register(r'clientes', ClienteViewSet)
router.register(r'empleados', EmpleadoViewSet)
router.register(r'productos', ProductoViewSet)
router.register(r'mesas', MesaViewSet)
router.register(r'pedidos', PedidoViewSet)
router.register(r'detalle-pedidos', DetallePedidoViewSet)
router.register(r'facturas', FacturaViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_view, name='login'),          # Ruta principal muestra el login
    path('dashboard/', views.dashboard_view, name='dashboard'), # Ruta del dashboard
    path('logout/', views.logout_view, name='logout'), # Ruta para cerrar sesión
    path('inventario/', views.inventario_view, name='inventario'), # Ruta para el inventario
    path('nuevo-pedido/', views.crear_pedido_view, name='crear_pedido'), # Ruta para crear un nuevo pedido mesero
    path('cocina/', views.cocina_view, name='cocina'),
    path('facturacion/', views.facturacion_view, name='facturacion'),
    path('pedido/<int:id_pedido>/pagar/', views.pagar_pedido_api, name='pagar_pedido_api'),
    path('pedido/<int:id_pedido>/iniciar/', views.iniciar_preparacion_api, name='iniciar_preparacion'),
    path('pedido/<int:id_pedido>/completar/', views.completar_pedido_api, name='completar_pedido_api'),

    path('inventario/ajustar-stock/<int:id_producto>/', views.ajustar_stock_view, name='ajustar_stock'),
    path('inventario/eliminar-producto/<int:id_producto>/', views.eliminar_producto_view, name='eliminar_producto'),
    path('api/pedidos-cocina/', views.api_pedidos_cocina, name='api_pedidos_cocina'),

    path('clientes/', views.clientes_view, name='clientes'), # Ruta para listar y crear clientes
    path('clientes/editar/<int:id_cliente>/', views.editar_cliente_view, name='editar_cliente'),
    path('clientes/eliminar/<int:id_cliente>/', views.eliminar_cliente_view, name='eliminar_cliente'),

    path('personal/', views.personal_view, name='personal'), # Ruta para listar y crear empleados
    path('personal/editar/<int:id_empleado>/', views.editar_empleado_view, name='editar_empleado'),
    path('personal/eliminar/<int:id_empleado>/', views.eliminar_empleado_view, name='eliminar_empleado'),

    path('api/', include(router.urls)),
]    