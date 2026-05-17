from django import forms
from .models import Pedido, Empleado

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido 
        # Los campos que el mesero podrá llenar:
        fields = ['id_empleado', 'id_mesa', 'tipo_pedido', 'observaciones', 'total']
        
        # Le ponemos clases de diseño para que se vea bien
        widgets = {
            'tipo_pedido': forms.TextInput(attrs={'class': 'validate'}),
            'observaciones': forms.Textarea(attrs={'class': 'materialize-textarea'}),
            'total': forms.NumberInput(attrs={'class': 'validate'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtramos la caja de empleados: Solo los que su cargo se llame "Mesero"
        self.fields['id_empleado'].queryset = Empleado.objects.filter(id_cargo__nombre='Mesero')