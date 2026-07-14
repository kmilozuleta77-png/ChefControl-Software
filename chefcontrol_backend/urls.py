from django.contrib import admin
from django.urls import path
from restaurante import views  # Importamos las vistas que acabamos de crear

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
    path('api/pedidos-cocina/', views.api_pedidos_cocina, name='api_pedidos_cocina'),
]    