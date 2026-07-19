from rest_framework import serializers
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


class CargoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cargo
        fields = '__all__'


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'


class EmpleadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empleado
        fields = '__all__'


class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'

    def validate_precio(self, value):
        """
        Rechaza precios en cero o negativos: un producto no puede
        venderse gratis ni a precio inválido.
        """
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser mayor que cero.")
        return value


class MesaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mesa
        fields = '__all__'


class PedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = '__all__'


class DetallePedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Detallepedido
        fields = '__all__'


class FacturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Factura
        fields = '__all__'

    def validate_metodo_pago(self, value):
        """
        Valida que el método de pago sea uno de los valores permitidos,
        con el mismo criterio que METODOS_PAGO_DB en views.py.
        """
        metodos_validos = ['Efectivo', 'Tarjeta Débito', 'Tarjeta Crédito', 'Transferencia']
        if value and value not in metodos_validos:
            raise serializers.ValidationError(
                f"Método de pago inválido. Debe ser uno de: {', '.join(metodos_validos)}."
            )
        return value