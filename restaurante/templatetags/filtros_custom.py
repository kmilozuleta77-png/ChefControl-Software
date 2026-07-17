from django import template

register = template.Library()


@register.filter(name='formato_cop')
def formato_cop(valor):
    """Convierte un Decimal a formato moneda colombiana sin decimales. Ej: 50000.00 → $50.000"""
    if valor is None:
        return '$0'
    try:
        entero = int(valor)
    except (ValueError, TypeError):
        return '$0'
    return '$' + f'{entero:,}'.replace(',', '.')
