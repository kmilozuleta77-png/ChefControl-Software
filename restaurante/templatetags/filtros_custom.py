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


@register.filter(name='get_item')
def get_item(diccionario, clave):
    """Accede a un valor de diccionario usando una clave dinámica (variable de un {% for %}),
    algo que Django no permite con la notación de punto habitual ({{ dict.clave }})."""
    if not diccionario:
        return 0
    return diccionario.get(clave, 0)
