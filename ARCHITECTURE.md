# Arquitectura — ChefControl

## Visión general

ChefControl sigue el patrón **MVC clásico de Django** (Model → View → Template).
El esquema de base de datos está gestionado **directamente en MySQL** mediante un
script SQL; todos los modelos de negocio usan `managed=False`, lo que significa
que Django no crea ni altera esas tablas — solo las lee y escribe a través del ORM.

```
Browser ──HTTP──► Django (urls.py → views.py) ──ORM──► MySQL
                       │
                  templates/ ◄── context dict
```

---

## Flujo de datos principal

```
[Login]
  │  authenticate(username, password)
  ▼
[Dashboard]  métricas: ventas del día, pedidos activos, alertas de inventario
  │
  ▼
[POS — nuevo-pedido/]
  │  POST: empleado + mesa + lista de productos + cantidades
  │  transaction.atomic → INSERT pedido + N INSERT detallepedido
  ▼
[KDS — cocina/]
  │  GET: pedidos con estado "Pendiente" o "En Preparación"
  │  Polling cada 15 s → GET /api/pedidos-cocina/ (JSON)
  │  Cocinero confirma → POST /pedido/<id>/completar/ → estado = "Listo"
  ▼
[Caja — facturacion/]
  │  GET: pedidos con estado "Listo"
  │  Cajero cobra → POST /pedido/<id>/pagar/
  │  INSERT factura → estado pedido = "Pagado"
  ▼
[Inventario / Reportes / Admin]
  (en desarrollo)
```

---

## Modelos de negocio y relaciones

> Todos los modelos tienen `managed = False` y mapean tablas definidas en
> `chefcontrol_database/chefcontrol_database.sql`.

```
Cargo ◄──FK── Empleado ──────────────────────────────┐
                                                       │
Categoria ◄──FK── Producto ──────────────────┐        │
                                              │        │
Mesa ────────────────────────────────┐        │        │
                                     │        │        │
Cliente ─────────────────────────────┤        │        │
                                     ▼        │        │
                                  Pedido ─────┘        │
                                     │                 │
                              PROTECT│                 │
                                     ▼                 │
                              Detallepedido            │
                                                       │
                              Pedido ──OneToOne──► Factura
                                                       │
                                             PROTECT   │
                                                       └── Empleado
```

### Detalle de cada modelo

| Modelo | Tabla MySQL | Campos clave | Notas |
|---|---|---|---|
| `Cargo` | `cargo` | `id_cargo`, `nombre`, `descripcion` | Roles: Mesero, Cocinero, Cajero, Administrador |
| `Empleado` | `empleado` | `id_empleado`, `id_cargo` (FK), `nombres`, `apellidos`, `cedula`, `estado` | Vinculado a usuario Django para autenticación |
| `Cliente` | `cliente` | `id_cliente`, `nombres`, `apellidos`, `cedula`, `email`, `telefono` | Nullable en Pedido (soporta "para llevar") |
| `Mesa` | `mesa` | `id_mesa`, `numero_mesa`, `capacidad`, `estado` | Estados: Disponible · Ocupada · Reservada |
| `Categoria` | `categoria` | `id_categoria`, `nombre` | Agrupa productos del menú |
| `Producto` | `producto` | `id_producto`, `id_categoria` (FK), `nombre`, `precio`, `stock`, `stock_minimo` | Índice en `stock` para alertas |
| `Pedido` | `pedido` | `id_pedido`, `id_empleado` (FK), `id_cliente` (nullable FK), `id_mesa` (nullable FK), `estado`, `tipo_pedido`, `total` | Estados: Pendiente · En Preparación · Listo · Entregado · Cancelado |
| `Detallepedido` | `detallepedido` | `id_detalle`, `id_pedido` (FK PROTECT), `id_producto` (FK PROTECT), `cantidad`, `precio_unitario` | PROTECT preserva historial contable |
| `Factura` | `factura` | `id_factura`, `id_pedido` (OneToOne PROTECT), `id_empleado` (FK), `subtotal`, `impuesto`, `descuento`, `total`, `metodo_pago` | PROTECT impide borrar pedido ya facturado |

### Índices de optimización

```sql
-- Acelera alertas de inventario (WHERE stock <= stock_minimo)
idx_producto_stock     ON producto(stock)

-- Acelera KDS y caja (WHERE estado = 'Pendiente' / 'Listo')
idx_pedido_estado      ON pedido(estado)

-- Acelera ordenamiento por fecha en dashboard y KDS
idx_pedido_fecha_desc  ON pedido(fecha_pedido DESC)
```

### Vistas SQL (reporting)

```sql
v_pedidos_detalle       -- Pedidos con info completa: cliente, empleado, mesa
v_productos_inventario  -- Productos con categoría y flag de alerta de stock
v_ventas_empleado       -- Reporte de ventas agrupado por empleado
```

---

## Estructura de carpetas

```
ChefControl Software/
│
├── chefcontrol_backend/          # Configuración principal de Django
│   ├── settings.py               # BD, seguridad, logging, locale (es-co / Bogotá)
│   ├── urls.py                   # 11 rutas del sistema (ver tabla en README)
│   ├── wsgi.py                   # Punto de entrada WSGI (producción)
│   └── asgi.py                   # Punto de entrada ASGI (async)
│
├── restaurante/                  # Aplicación Django principal
│   ├── models.py                 # 9 modelos de negocio + tablas internas Django
│   ├── views.py                  # 7 vistas + 3 mini-APIs
│   ├── forms.py                  # PedidoForm (validación HTML)
│   ├── admin.py                  # Registro en panel admin
│   ├── apps.py                   # Configuración de la app
│   ├── tests.py                  # Tests (pendiente implementar)
│   └── migrations/               # Solo __init__.py; esquema en MySQL
│
├── chefcontrol_database/
│   └── chefcontrol_database.sql  # Script completo: tablas, índices, vistas, seeds
│
├── templates/                    # Plantillas HTML (Django Templates)
│   ├── login.html                # ✅ Dark Premium
│   ├── index.html                # 🔧 Dashboard (requiere rediseño)
│   ├── crear_pedido.html         # ✅ POS con carrito
│   ├── cocina.html               # ✅ KDS con polling
│   ├── facturacion.html          # ✅ Terminal de caja
│   ├── inventario.html           # 🔧 Diseño parcial
│   ├── pedidos.html              # ⚠️ Diseño antiguo
│   ├── menus.html                # ⚠️ Sin conexión a BD
│   ├── clientes.html             # ⚠️ Sin conexión a BD
│   ├── personal.html             # ⚠️ Sin conexión a BD
│   ├── reportes.html             # ⚠️ Sin conexión a BD
│   └── configuracion.html        # ⚠️ Sin conexión a BD
│
├── static/
│   ├── CSS/
│   │   └── custom-styles.css     # Sistema de diseño Dark Premium (~19 KB)
│   ├── JS/
│   │   └── app.js                # Inicializaciones Materialize + utilidades
│   └── IMAGES/                   # Logos e imágenes del proyecto
│
├── logs/
│   └── chefcontrol.log           # Log de la aplicación (WARNING/ERROR)
│
├── manage.py                     # CLI de Django
├── requirements.txt              # Dependencias Python con versiones exactas
├── .env                          # Variables de entorno (NO versionado)
├── .gitignore
├── README.md
├── ARCHITECTURE.md               # (este archivo)
└── TASKS.md
```

---

## Vistas y mini-APIs

| Vista/API | Método | Ruta | Rol requerido | Descripción |
|---|---|---|---|---|
| `login_view` | GET/POST | `/` | — | Autenticación |
| `logout_view` | GET | `/logout/` | Cualquiera | Cierre de sesión |
| `dashboard_view` | GET | `/dashboard/` | Cualquiera | Métricas generales |
| `inventario_view` | GET | `/inventario/` | Admin/Cajero | Gestión de stock |
| `crear_pedido_view` | GET/POST | `/nuevo-pedido/` | Mesero | POS: crear pedido |
| `cocina_view` | GET | `/cocina/` | Cocinero | KDS: pedidos activos |
| `facturacion_view` | GET | `/facturacion/` | Cajero | Caja: pedidos listos |
| `api_pedidos_cocina` | GET | `/api/pedidos-cocina/` | Cocinero | JSON: pedidos pendientes |
| `completar_pedido_api` | POST | `/pedido/<id>/completar/` | Cocinero | Estado → Listo |
| `pagar_pedido_api` | POST | `/pedido/<id>/pagar/` | Cajero | Estado → Pagado |

---

## Patrones de código

### Control de acceso por rol

```python
# Decorador personalizado — restringe la vista a los cargos indicados
@requiere_rol('Mesero', 'Administrador')
def crear_pedido_view(request):
    ...
```

### Atomicidad en creación de pedidos

```python
with transaction.atomic():
    pedido = Pedido.objects.create(...)
    for item in items:
        Detallepedido.objects.create(id_pedido=pedido, ...)
```

### Optimización de consultas (evita N+1)

```python
Pedido.objects.select_related('id_cliente', 'id_empleado', 'id_mesa') \
              .prefetch_related('detallepedido_set__id_producto')
```

### Logging estructurado

```python
import logging
logger = logging.getLogger(__name__)

logger.warning("Intento fallido de login: %s", username)
logger.error("Error al procesar pedido: %s", str(e))
# Salida → logs/chefcontrol.log y consola (nivel DEBUG en desarrollo)
```

---

## Sistema de diseño Dark Premium (frontend)

**Archivo**: `static/CSS/custom-styles.css`

| Variable CSS | Valor | Uso |
|---|---|---|
| `--bg-base` | `#0a0a0a` | Fondo principal |
| `--bg-surface` | `#111111` | Tarjetas, paneles |
| `--bg-elevated` | `#1a1a1a` | Modales, dropdowns |
| `--accent` | `#f97316` | Naranja — acción primaria |
| `--accent-hover` | `#ea6c0a` | Hover sobre acento |
| `--text-primary` | `#f5f5f5` | Texto principal |
| `--text-secondary` | `#a3a3a3` | Texto secundario |
| `--border` | `#2a2a2a` | Bordes sutiles |
| `--success` | `#22c55e` | Confirmaciones |
| `--danger` | `#ef4444` | Errores y cancelaciones |

**Íconos**: Material Icons (Google Fonts CDN)
**Framework CSS**: Materialize CSS (migración en progreso hacia CSS custom puro)

---

## Seguridad

| Medida | Detalle |
|---|---|
| `SECRET_KEY` | En `.env`, nunca en el código |
| `DEBUG` | `True` en desarrollo, `False` en producción (desde `.env`) |
| CSRF | `django.middleware.csrf.CsrfViewMiddleware` activo |
| SSL / HSTS | `SECURE_SSL_REDIRECT=True` + `HSTS` cuando `DEBUG=False` |
| Errores | Mensajes genéricos al cliente; detalles solo en logs |
| Contraseñas | Gestionadas por el sistema de auth de Django (hash PBKDF2) |
| Locale | `es-co` · Zona horaria: `America/Bogota` |
