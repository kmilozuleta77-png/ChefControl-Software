from rest_framework import viewsets

from .models import (
    Cargo,
    Categoria,
    Cliente,
    Empleado,
    Producto,
    Mesa,
    Pedido,
    Detallepedido,
    Factura
)

from .serializers import (
    CargoSerializer,
    CategoriaSerializer,
    ClienteSerializer,
    EmpleadoSerializer,
    ProductoSerializer,
    MesaSerializer,
    PedidoSerializer,
    DetallePedidoSerializer,
    FacturaSerializer
)


class CargoViewSet(viewsets.ModelViewSet):
    queryset = Cargo.objects.all()
    serializer_class = CargoSerializer


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer


class EmpleadoViewSet(viewsets.ModelViewSet):
    queryset = Empleado.objects.all()
    serializer_class = EmpleadoSerializer


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer


class MesaViewSet(viewsets.ModelViewSet):
    queryset = Mesa.objects.all()
    serializer_class = MesaSerializer


class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer


class DetallePedidoViewSet(viewsets.ModelViewSet):
    queryset = Detallepedido.objects.all()
    serializer_class = DetallePedidoSerializer


class FacturaViewSet(viewsets.ModelViewSet):
    queryset = Factura.objects.all()
    serializer_class = FacturaSerializer