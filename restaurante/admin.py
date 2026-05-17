from django.contrib import admin
from .models import Cargo, Categoria, Cliente, Empleado, Mesa, Pedido, Producto, Factura

# Registramos todas nuestras tablas para que aparezcan en el panel de control
admin.site.register(Cargo)
admin.site.register(Categoria)
admin.site.register(Cliente)
admin.site.register(Empleado)
admin.site.register(Mesa)
admin.site.register(Pedido)
admin.site.register(Producto)
admin.site.register(Factura)