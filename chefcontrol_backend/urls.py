from django.contrib import admin
from django.urls import path
from restaurante import views  # Importamos las vistas que acabamos de crear

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_view, name='login'),          # Ruta principal muestra el login
    path('dashboard/', views.dashboard_view, name='dashboard'), # Ruta del dashboard
    path('logout/', views.logout_view, name='logout'), # Ruta para cerrar sesión
    path('inventario/', views.inventario_view, name='inventario'), # Ruta para el inventario
]    