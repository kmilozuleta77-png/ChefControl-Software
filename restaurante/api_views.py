from rest_framework import viewsets

from .permissions import (
    EsAdministrador,
    EsAdministradorOCajero,
    EsAdministradorEscritura,
    EsPersonalOperativoPedidos,
)
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
    permission_classes = [EsAdministradorEscritura]


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [EsAdministradorEscritura]


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    # Sin restricción de rol: queda con IsAuthenticated global (decisión explícita)


class EmpleadoViewSet(viewsets.ModelViewSet):
    queryset = Empleado.objects.all()
    serializer_class = EmpleadoSerializer
    permission_classes = [EsAdministrador]


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [EsAdministradorEscritura]


class MesaViewSet(viewsets.ModelViewSet):
    queryset = Mesa.objects.all()
    serializer_class = MesaSerializer
    permission_classes = [EsAdministradorEscritura]


class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer
    permission_classes = [EsPersonalOperativoPedidos]


class DetallePedidoViewSet(viewsets.ModelViewSet):
    queryset = Detallepedido.objects.all()
    serializer_class = DetallePedidoSerializer
    permission_classes = [EsPersonalOperativoPedidos]


class FacturaViewSet(viewsets.ModelViewSet):
    queryset = Factura.objects.all()
    serializer_class = FacturaSerializer
    permission_classes = [EsAdministradorOCajero]