# API REST — ChefControl

Documentación de los 9 servicios REST expuestos por el proyecto ChefControl, generados con Django REST Framework mediante `DefaultRouter` (`chefcontrol_backend/urls.py`).

Evidencia académica: GA7-220501096-AA5-EV03.

---

## Autenticación

Todos los endpoints de esta API requieren **sesión iniciada**. La configuración global está en `chefcontrol_backend/settings.py`:

```python
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
}
```

Esto significa que:

- No hay tokens ni API Keys: la autenticación se hace mediante la cookie de sesión de Django (`sessionid`), obtenida al iniciar sesión desde `/` (`views.login_view`).
- Cualquier request sin sesión activa recibe `403 Forbidden` (`{"detail": "Authentication credentials were not provided."}` o `"You do not have permission to perform this action."` según el caso).
- Al ser `SessionAuthentication`, las peticiones que modifican estado (POST/PUT/PATCH/DELETE) desde un cliente externo deben incluir el header `X-CSRFToken` además de la cookie de sesión.

## Nota sobre el alcance de esta API

Los recursos **Pedido**, **DetallePedido** y **Factura** exponen aquí un **CRUD genérico** (`ModelViewSet` estándar de DRF), pensado para consumo externo, integraciones o herramientas de administración.

El **flujo de negocio real** de la aplicación **no pasa por estos endpoints**, sino por vistas dedicadas fuera de esta API, que sí aplican las reglas de negocio:

- `crear_pedido_view` — crea un pedido completo (cabecera + detalles) dentro de una **transacción atómica**, validando stock disponible antes de descontar inventario.
- `pagar_pedido_api` — liquida un pedido calculando impuestos y generando la factura correspondiente.
- `iniciar_preparacion_api` / `completar_pedido_api` — transiciones de estado del flujo de cocina (KDS).

Es decir: el CRUD de `/api/pedidos/`, `/api/detalle-pedidos/` y `/api/facturas/` permite crear/editar registros de forma directa, pero **sin** las validaciones de stock, cálculo de impuestos ni consistencia transaccional que sí aplican las vistas de negocio. Esto es una decisión de diseño: la API REST es una capa de datos genérica; la lógica de dominio vive en la capa de vistas de la aplicación.

## Nota de privacidad en los ejemplos

Los ejemplos JSON de este documento provienen de consultas reales a la base de datos de pruebas del proyecto. Sin embargo, en los recursos **Cliente** y **Empleado** los valores de `nombres`, `apellidos`, `cedula`, `telefono`, `direccion` y `email` fueron **reemplazados por datos ficticios genéricos** para no exponer información personal identificable en un documento de entrega académica. La estructura, los tipos de dato y los demás campos (fechas, estados, montos, relaciones) sí corresponden a registros reales.

---

## 1. Cargo

**Endpoint base:** `/api/cargos/`

| Método | URL | Acción |
|---|---|---|
| GET | `/api/cargos/` | Listar todos los cargos |
| POST | `/api/cargos/` | Crear un cargo |
| GET | `/api/cargos/<id_cargo>/` | Detalle de un cargo |
| PUT/PATCH | `/api/cargos/<id_cargo>/` | Actualizar un cargo |
| DELETE | `/api/cargos/<id_cargo>/` | Eliminar un cargo |

### Campos (modelo `Cargo`)

| Campo | Tipo | Obligatorio |
|---|---|---|
| `id_cargo` | entero (autogenerado, PK) | No (solo lectura) |
| `nombre` | texto, máx. 50, único | **Sí** |
| `descripcion` | texto, máx. 200 | No |
| `fecha_creacion` | fecha y hora | No |

### Validaciones personalizadas

Ninguna (`fields = '__all__'` sin `validate_<campo>`).

### Ejemplo de respuesta (`GET /api/cargos/1/`)

```json
{
    "id_cargo": 1,
    "nombre": "Administrador",
    "descripcion": "Gestiona y supervisa todas las operaciones del restaurante",
    "fecha_creacion": "2026-03-01T13:32:42Z"
}
```

---

## 2. Categoria

**Endpoint base:** `/api/categorias/`

| Método | URL | Acción |
|---|---|---|
| GET | `/api/categorias/` | Listar todas las categorías |
| POST | `/api/categorias/` | Crear una categoría |
| GET | `/api/categorias/<id_categoria>/` | Detalle de una categoría |
| PUT/PATCH | `/api/categorias/<id_categoria>/` | Actualizar una categoría |
| DELETE | `/api/categorias/<id_categoria>/` | Eliminar una categoría |

### Campos (modelo `Categoria`)

| Campo | Tipo | Obligatorio |
|---|---|---|
| `id_categoria` | entero (autogenerado, PK) | No (solo lectura) |
| `nombre` | texto, máx. 50, único | **Sí** |
| `descripcion` | texto, máx. 200 | No |
| `fecha_creacion` | fecha y hora | No |

### Validaciones personalizadas

Ninguna.

### Ejemplo de respuesta (`GET /api/categorias/1/`)

```json
{
    "id_categoria": 1,
    "nombre": "Entradas",
    "descripcion": "Platos de entrada y aperitivos",
    "fecha_creacion": "2026-03-01T13:32:42Z"
}
```

---

## 3. Cliente

**Endpoint base:** `/api/clientes/`

| Método | URL | Acción |
|---|---|---|
| GET | `/api/clientes/` | Listar todos los clientes |
| POST | `/api/clientes/` | Crear un cliente |
| GET | `/api/clientes/<id_cliente>/` | Detalle de un cliente |
| PUT/PATCH | `/api/clientes/<id_cliente>/` | Actualizar un cliente |
| DELETE | `/api/clientes/<id_cliente>/` | Eliminar un cliente |

### Campos (modelo `Cliente`)

| Campo | Tipo | Obligatorio |
|---|---|---|
| `id_cliente` | entero (autogenerado, PK) | No (solo lectura) |
| `nombres` | texto, máx. 100 | **Sí** |
| `apellidos` | texto, máx. 100 | **Sí** |
| `cedula` | texto, máx. 20, único | No |
| `telefono` | texto, máx. 20 | No |
| `email` | texto, máx. 100, único | No |
| `direccion` | texto, máx. 200 | No |
| `estado` | texto, máx. 8 | No |
| `fecha_creacion` | fecha y hora | No |

### Validaciones personalizadas

Ninguna.

### Ejemplo de respuesta (`GET /api/clientes/1/`)

```json
{
    "id_cliente": 1,
    "nombres": "Carlos",
    "apellidos": "Ramírez",
    "cedula": "1000000001",
    "telefono": "3000000001",
    "email": null,
    "direccion": "Calle 10 # 20-30",
    "estado": "Activo",
    "fecha_creacion": "2026-03-15T00:00:00Z"
}
```

---

## 4. Empleado

**Endpoint base:** `/api/empleados/`

| Método | URL | Acción |
|---|---|---|
| GET | `/api/empleados/` | Listar todos los empleados |
| POST | `/api/empleados/` | Crear un empleado |
| GET | `/api/empleados/<id_empleado>/` | Detalle de un empleado |
| PUT/PATCH | `/api/empleados/<id_empleado>/` | Actualizar un empleado |
| DELETE | `/api/empleados/<id_empleado>/` | Eliminar un empleado |

### Campos (modelo `Empleado`)

| Campo | Tipo | Obligatorio |
|---|---|---|
| `id_empleado` | entero (autogenerado, PK) | No (solo lectura) |
| `id_cargo` | FK → `Cargo` | **Sí** |
| `nombres` | texto, máx. 100 | **Sí** |
| `apellidos` | texto, máx. 100 | **Sí** |
| `cedula` | texto, máx. 20, único | **Sí** |
| `telefono` | texto, máx. 20 | No |
| `email` | texto, máx. 100, único | No |
| `direccion` | texto, máx. 200 | No |
| `fecha_ingreso` | fecha | **Sí** |
| `estado` | texto, máx. 8 | No |
| `fecha_creacion` | fecha y hora | No |

### Validaciones personalizadas

Ninguna.

### Ejemplo de respuesta (`GET /api/empleados/1/`)

```json
{
    "id_empleado": 1,
    "id_cargo": 1,
    "nombres": "Ana María",
    "apellidos": "Torres",
    "cedula": "1000000002",
    "telefono": "3000000002",
    "email": "empleado@chefcontrol.com",
    "direccion": "Carrera 45 # 12-34",
    "fecha_ingreso": "2026-05-17",
    "estado": "Activo",
    "fecha_creacion": "2026-05-17T10:41:14Z"
}
```

---

## 5. Producto

**Endpoint base:** `/api/productos/`

| Método | URL | Acción |
|---|---|---|
| GET | `/api/productos/` | Listar todos los productos |
| POST | `/api/productos/` | Crear un producto |
| GET | `/api/productos/<id_producto>/` | Detalle de un producto |
| PUT/PATCH | `/api/productos/<id_producto>/` | Actualizar un producto |
| DELETE | `/api/productos/<id_producto>/` | Eliminar un producto |

### Campos (modelo `Producto`)

| Campo | Tipo | Obligatorio |
|---|---|---|
| `id_producto` | entero (autogenerado, PK) | No (solo lectura) |
| `id_categoria` | FK → `Categoria` | **Sí** |
| `nombre` | texto, máx. 100 | **Sí** |
| `descripcion` | texto, máx. 300 | No |
| `precio` | decimal (10 dígitos, 2 decimales) | **Sí** |
| `stock` | entero | No |
| `stock_minimo` | entero | No |
| `imagen` | texto, máx. 255 | No |
| `estado` | texto, máx. 13 | No |
| `fecha_creacion` | fecha y hora | No |

### Validaciones personalizadas

`validate_precio` (`restaurante/serializers.py:44-51`): rechaza `precio <= 0`.

```python
def validate_precio(self, value):
    if value <= 0:
        raise serializers.ValidationError("El precio debe ser mayor que cero.")
    return value
```

Un `POST`/`PUT` con `"precio": 0` o `"precio": -5000` responde `400 Bad Request`:

```json
{
    "precio": ["El precio debe ser mayor que cero."]
}
```

### Ejemplo de respuesta (`GET /api/productos/1/`)

```json
{
    "id_producto": 1,
    "id_categoria": 1,
    "nombre": "Patatas Bravas",
    "descripcion": null,
    "precio": "10000.00",
    "stock": 36,
    "stock_minimo": 5,
    "imagen": null,
    "estado": "Disponible",
    "fecha_creacion": "2026-05-17T14:07:25Z"
}
```

---

## 6. Mesa

**Endpoint base:** `/api/mesas/`

| Método | URL | Acción |
|---|---|---|
| GET | `/api/mesas/` | Listar todas las mesas |
| POST | `/api/mesas/` | Crear una mesa |
| GET | `/api/mesas/<id_mesa>/` | Detalle de una mesa |
| PUT/PATCH | `/api/mesas/<id_mesa>/` | Actualizar una mesa |
| DELETE | `/api/mesas/<id_mesa>/` | Eliminar una mesa |

### Campos (modelo `Mesa`)

| Campo | Tipo | Obligatorio |
|---|---|---|
| `id_mesa` | entero (autogenerado, PK) | No (solo lectura) |
| `numero_mesa` | entero, único | **Sí** |
| `capacidad` | entero | **Sí** |
| `estado` | texto, máx. 16 | No |
| `ubicacion` | texto, máx. 100 | No |
| `fecha_creacion` | fecha y hora | No |

### Validaciones personalizadas

Ninguna.

### Ejemplo de respuesta (`GET /api/mesas/1/`)

```json
{
    "id_mesa": 1,
    "numero_mesa": 1,
    "capacidad": 2,
    "estado": "Disponible",
    "ubicacion": "Zona Interior",
    "fecha_creacion": "2026-03-01T13:32:42Z"
}
```

---

## 7. Pedido

**Endpoint base:** `/api/pedidos/`

> CRUD genérico — ver "Nota sobre el alcance de esta API" al inicio del documento. El flujo real de creación de pedidos vive en `crear_pedido_view`.

| Método | URL | Acción |
|---|---|---|
| GET | `/api/pedidos/` | Listar todos los pedidos |
| POST | `/api/pedidos/` | Crear un pedido |
| GET | `/api/pedidos/<id_pedido>/` | Detalle de un pedido |
| PUT/PATCH | `/api/pedidos/<id_pedido>/` | Actualizar un pedido |
| DELETE | `/api/pedidos/<id_pedido>/` | Eliminar un pedido |

### Campos (modelo `Pedido`)

| Campo | Tipo | Obligatorio |
|---|---|---|
| `id_pedido` | entero (autogenerado, PK) | No (solo lectura) |
| `id_cliente` | FK → `Cliente` | No (nulo = pedido "para llevar" sin cliente registrado) |
| `id_empleado` | FK → `Empleado` | **Sí** |
| `id_mesa` | FK → `Mesa` | No (nulo = pedido "para llevar" sin mesa) |
| `fecha_pedido` | fecha y hora | No |
| `estado` | texto, máx. 14 | No |
| `tipo_pedido` | texto, máx. 11 | No |
| `observaciones` | texto, máx. 500 | No |
| `total` | decimal (10 dígitos, 2 decimales) | No |

### Validaciones personalizadas

Ninguna (la validación de stock y cálculo de total ocurre en `crear_pedido_view`, no en este serializer).

### Ejemplo de respuesta (`GET /api/pedidos/1/`)

```json
{
    "id_pedido": 1,
    "id_cliente": 1,
    "id_empleado": 1,
    "id_mesa": 1,
    "fecha_pedido": "2026-05-17T10:51:17Z",
    "estado": "Pagado",
    "tipo_pedido": null,
    "observaciones": null,
    "total": "50000.00"
}
```

---

## 8. DetallePedido

**Endpoint base:** `/api/detalle-pedidos/`

> CRUD genérico — ver "Nota sobre el alcance de esta API" al inicio del documento.

| Método | URL | Acción |
|---|---|---|
| GET | `/api/detalle-pedidos/` | Listar todos los detalles de pedido |
| POST | `/api/detalle-pedidos/` | Crear un detalle de pedido |
| GET | `/api/detalle-pedidos/<id_detalle>/` | Detalle de un renglón |
| PUT/PATCH | `/api/detalle-pedidos/<id_detalle>/` | Actualizar un renglón |
| DELETE | `/api/detalle-pedidos/<id_detalle>/` | Eliminar un renglón |

### Campos (modelo `Detallepedido`)

| Campo | Tipo | Obligatorio |
|---|---|---|
| `id_detalle` | entero (autogenerado, PK) | No (solo lectura) |
| `id_pedido` | FK → `Pedido` (`on_delete=PROTECT`) | **Sí** |
| `id_producto` | FK → `Producto` (`on_delete=PROTECT`) | **Sí** |
| `cantidad` | entero | **Sí** |
| `precio_unitario` | decimal (10 dígitos, 2 decimales) | **Sí** |
| `observaciones` | texto, máx. 300 | No |

`PROTECT` en ambas relaciones: no se puede borrar un `Pedido` ni un `Producto` si tienen detalles asociados, preservando el historial y la integridad contable.

### Validaciones personalizadas

Ninguna.

### Ejemplo de respuesta (`GET /api/detalle-pedidos/1/`)

```json
{
    "id_detalle": 1,
    "id_pedido": 6,
    "id_producto": 1,
    "cantidad": 2,
    "precio_unitario": "10000.00",
    "observaciones": null
}
```

---

## 9. Factura

**Endpoint base:** `/api/facturas/`

> CRUD genérico — ver "Nota sobre el alcance de esta API" al inicio del documento. El cálculo de impuestos y la liquidación real ocurren en `pagar_pedido_api`.

| Método | URL | Acción |
|---|---|---|
| GET | `/api/facturas/` | Listar todas las facturas |
| POST | `/api/facturas/` | Crear una factura |
| GET | `/api/facturas/<id_factura>/` | Detalle de una factura |
| PUT/PATCH | `/api/facturas/<id_factura>/` | Actualizar una factura |
| DELETE | `/api/facturas/<id_factura>/` | Eliminar una factura |

### Campos (modelo `Factura`)

| Campo | Tipo | Obligatorio |
|---|---|---|
| `id_factura` | entero (autogenerado, PK) | No (solo lectura) |
| `id_pedido` | FK 1-a-1 → `Pedido` (`on_delete=PROTECT`) | **Sí** |
| `id_empleado` | FK → `Empleado` | **Sí** |
| `fecha_factura` | fecha y hora | No |
| `subtotal` | decimal (10 dígitos, 2 decimales) | **Sí** |
| `impuesto` | decimal (10 dígitos, 2 decimales) | No |
| `descuento` | decimal (10 dígitos, 2 decimales) | No |
| `total` | decimal (10 dígitos, 2 decimales) | **Sí** |
| `metodo_pago` | texto, máx. 15 | No |
| `estado` | texto, máx. 9 | No |
| `observaciones` | texto, máx. 300 | No |

`PROTECT` en `id_pedido`: no se puede borrar un `Pedido` que ya tiene factura emitida (regla contable).

### Validaciones personalizadas

`validate_metodo_pago` (`restaurante/serializers.py:77-87`): si se envía `metodo_pago`, debe ser uno de los valores del ENUM.

```python
def validate_metodo_pago(self, value):
    metodos_validos = ['Efectivo', 'Tarjeta Débito', 'Tarjeta Crédito', 'Transferencia']
    if value and value not in metodos_validos:
        raise serializers.ValidationError(
            f"Método de pago inválido. Debe ser uno de: {', '.join(metodos_validos)}."
        )
    return value
```

Un `POST`/`PUT` con `"metodo_pago": "Bitcoin"` responde `400 Bad Request`:

```json
{
    "metodo_pago": ["Método de pago inválido. Debe ser uno de: Efectivo, Tarjeta Débito, Tarjeta Crédito, Transferencia."]
}
```

### Ejemplo de respuesta (`GET /api/facturas/1/`)

```json
{
    "id_factura": 1,
    "id_pedido": 15,
    "id_empleado": 1,
    "fecha_factura": "2026-06-21T11:38:58Z",
    "subtotal": "55558.80",
    "impuesto": "4444.70",
    "descuento": null,
    "total": "60003.50",
    "metodo_pago": "Tarjeta Crédito",
    "estado": "Pagada",
    "observaciones": "Tiquete POS"
}
```
