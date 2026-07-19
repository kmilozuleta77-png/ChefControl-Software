# TASKS â€” ChefControl

Lista de verificaciÃ³n de trabajo organizada por mÃ³dulo.
Actualiza este archivo al completar o agregar tareas.

- `[x]` Completado
- `[ ]` Pendiente
- `[~]` En progreso / parcial

---

## ðŸ” AutenticaciÃ³n y Seguridad

- [x] Login con usuario y contraseÃ±a (sistema auth de Django)
- [x] Control de acceso por rol â€” decorador `@requiere_rol()`
- [x] ProtecciÃ³n de vistas con `@login_required`
- [x] `SECRET_KEY` y credenciales de BD en `.env` (nunca en cÃ³digo)
- [x] `DEBUG` condicional segÃºn entorno
- [x] Logging estructurado en `logs/chefcontrol.log`
- [x] Errores sanitizados (mensajes genÃ©ricos al cliente, detalles en logs)
- [x] Middleware de seguridad Django (CSRF, XFrame, SessionSecurity)
- [ ] Headers de producciÃ³n activados y verificados (`SECURE_SSL_REDIRECT`, HSTS)
- [ ] Rate limiting en el endpoint de login (protecciÃ³n fuerza bruta)
- [ ] PolÃ­tica de contraseÃ±as (longitud mÃ­nima, complejidad)
- [ ] IsAuthenticated es piso, no rol — Mesero puede hacer CRUD completo
  sobre EmpleadoViewSet y FacturaViewSet vía /api/ (llevar @requiere_rol
  o permission_classes por ViewSet a los recursos sensibles)
- [ ] settings.py: eliminar bloque DATABASES hardcodeado (líneas 88-92,
  incluye password en texto plano) — sobrescrito por os.getenv pero
  sigue commiteado en el repo; avisar a Sofía para rotar la contraseña
  de MySQL expuesta en el historial de git

---

## ðŸŽ¨ UI Dark Premium

### Pantallas completadas
- [x] `login.html` â€” DiseÃ±o Dark Premium
- [x] `cocina.html` â€” KDS Dark Premium con polling
- [x] `facturacion.html` â€” Terminal de caja Dark Premium
- [x] `inventario.html` â€” migrado a `extends base.html`; toasts de mensajes ya se ven al instante (19/07/2026)
- [x] Fix formulario ilegible: faltaba el `<link>` de `materialize.min.css` (causa real de selects sin estilo y columnas apiladas) + `custom-styles.css` ahora cubre `.input-field select` y el dropdown generado por `M.FormSelect.init()` (19/07/2026)
- [x] `inventario.html` â€” reescrito 100% en design-system.css, sin Materialize CSS/JS (sidebar, top-nav, stat-card, tabla, status-badge, modales propios) (19/07/2026)
- [x] Bug corregido: `stock_minimo|divisibleby:2` nunca calculaba la mitad del stock minimo (comparaba contra True/False); reemplazado por `{% widthratio %}` en el template (19/07/2026)
- [ ] Modal de confirmaciÃ³n "Eliminar" con Dark Premium implementado; falta CRUD real de Categorias/Precio avanzado

### Pantallas pendientes de rediseÃ±o
- [x] `index.html` â€” Dashboard Dark Premium âœ… â€” migrado a design-system.css, tema toggle, fuente A-/A+
- [x] `crear_pedido.html` â€” Revisar bug: menÃºs y meseros no cargan desde BD
- [ ] `pedidos.html` — Diseño antiguo, requiere migración + crear URL `name='pedidos'` en urls.py (enlace “Ver todos” del dashboard apunta aquí)
- [ ] `menus.html` â€” DiseÃ±o antiguo + sin conexiÃ³n a BD
- [x] `clientes.html` â€” CRUD completo (listar/crear/editar/soft-delete), migrado a design-system.css sin Materialize (19/07/2026)
- [ ] `personal.html` â€” Sin diseÃ±o Dark Premium ni conexiÃ³n a BD
- [ ] `reportes.html` â€” Sin diseÃ±o Dark Premium ni conexiÃ³n a BD
- [ ] `configuracion.html` â€” Sin diseÃ±o Dark Premium ni conexiÃ³n a BD

### Sistema de diseÃ±o global
- [x] `design-system.css` creado â€” fuente Ãºnica de verdad: tokens, sidebar, topbar, badges, botones, mesas, animaciones
- [x] Toggle oscuro / claro (sistema de temas global con CSS variables + localStorage)
- [x] BotÃ³n de accesibilidad A- / A+ (tamaÃ±o de fuente dinÃ¡mico + localStorage)
- [ ] Cambiar tipografÃ­a `Inter` por serif premium en toda la UI
- [ ] Adaptar logo al estilo minimalista Dark Premium
- [ ] Micro-interacciones y animaciones de transiciÃ³n entre vistas
- [ ] Responsive design validado en tablet y mÃ³vil

---

## ðŸ—ï¸ Backend / LÃ³gica de Negocio

### Flujo principal (implementado)
- [x] Crear pedido con `transaction.atomic` (validaciones, detalles)
- [x] API de cocina con polling â€” `api_pedidos_cocina`
- [x] Transición de estado en cocina: Pendiente → En Preparación (`iniciar_preparacion_api`) → Listo (`completar_pedido_api`, ahora exige que el pedido ya esté "En Preparación") (14/07/2026)
- [x] Registrar pago y emitir factura â€” `pagar_pedido_api`
- [x] Dashboard con mÃ©tricas: ventas del dÃ­a, alertas de stock, pedidos recientes

### CRUD de mÃ³dulos administrativos (pendiente)
- [ ] **Inventario**: CRUD completo de Productos (crear, editar, desactivar)
- [ ] **Inventario**: ajuste manual de stock (entradas y salidas)
- [ ] **MenÃºs**: CRUD de CategorÃ­as y Productos del menÃº
- [x] **Clientes**: CRUD completo con bÃºsqueda por cÃ©dula / email â€” soft-delete (estado='Inactivo', fk_pedido_cliente es ON DELETE SET NULL asÃ­ que no era obligatorio pero preserva trazabilidad) (19/07/2026)
- [ ] **Personal**: CRUD de Empleados y Cargos
- [ ] **Reportes**: vistas conectadas a BD usando `v_ventas_empleado`, `v_productos_inventario`
- [ ] **ConfiguraciÃ³n**: ajustes globales del sistema (nombre del local, IVA, etc.)

### Bugs conocidos
- [x] `crear_pedido_view`: menÃºs y meseros no cargan desde BD (revisar `GET` context)
- [x] `dashboard_view`: dashboard renderiza + datos reales BD (01/06/2026)
- [x] `fix/dashboard-pedidos-recientes`: título, formato COP, badges reales, alertas BD, modal Ver pedido (02/06/2026)
- [x] `fix/fechas-dashboard`: "Pedidos Hoy" = 0 — causa: `fecha_pedido` quedaba NULL + `__date` requiere `CONVERT_TZ` en MySQL (sin tablas cargadas). Fix: `fecha_pedido=timezone.now()` al crear pedido + `rango_dia()` con `__gte/__lt` en `dashboard_view` (04/06/2026)
- [x] fix(dashboard): corregir TypeError en modal Ver Pedido — IIFE movida a DOMContentLoaded (09/07/2026)
- Causa: `<script>` en línea 517 se ejecutaba antes de parsear `#modal-ver-pedido` (línea 657)
- [ ] Evaluar mover `<script>` de index.html al final de `</body>` o usar `defer` (evita el patrón de orden para todo el archivo, no urgente)
- [ ] **Deuda técnica menor**: cambiar `fecha_pedido` a `auto_now_add=True` en modelo `Pedido` para garantizar que nunca quede NULL sin depender de la vista
- [ ] **Deuda tecnica**: ampliar `Factura.metodo_pago` a `max_length=30` con migracion — coordinar con Sofia; hoy `'Tarjeta Credito'` ocupa 14 chars, cabe justo; riesgo si se agregan metodos mas largos
- [ ] **Deuda tecnica**: centralizar codigos de metodo de pago en constante JS compartida en `facturacion.html` — hoy el literal `'efectivo'` esta disperso en `calcularCambio()`, `abrirModal()` y `confirmarPago()`
- [ ] **Deuda tecnica**: convertir `Factura.estado` a campo `choices` — hoy `CharField(9)` libre; `'Pagada'` cabe justo, cualquier estado mas largo (ej. `'Pendiente'`) agota el limite
- [ ] **Deuda tecnica (pendiente hasta terminar Clientes/Empleados)**: extraer a `design-system.css` el bloque CSS de modales (`.modal-overlay`, `.modal-panel`, `.form-grid`, `.field-input`, etc.) duplicado igual en `index.html`, `inventario.html` y `clientes.html`
- [ ] **Deuda tecnica (pendiente hasta terminar Clientes/Empleados)**: extraer a un JS compartido el bloque de tema oscuro/claro, tamaño de fuente, reloj en vivo y toggle de sidebar, duplicado igual en `index.html`, `inventario.html` y `clientes.html`
- [x] **Deuda técnica**: normalizar estado `"En preparacion"` → `"En Preparación"` — corregido en views.py; no requirió migración porque el estado nunca llegó a asignarse en BD (14/07/2026)
- [x] index.html no mostraba {% for message in messages %} — creado templates/base.html con toast de mensajes Django (error/warning 8s, success/info 6s) e index.html migrado a extends; resto de templates queda pendiente de migrar (18/07/2026)

### Mejoras de lÃ³gica
- [ ] Propina de monto libre en facturaciÃ³n (actualmente solo porcentaje)
- [ ] Tipos de pedido: implementar lÃ³gica para "Para llevar" y "Domicilio"
- [ ] PaginaciÃ³n en historial de pedidos y reportes
- [ ] BÃºsqueda y filtros en mÃ³dulo de inventario
- [ ] Exportar reportes a PDF / Excel

---

## ðŸ’… UX / Accesibilidad

- [ ] Toggle modo oscuro / claro global con persistencia en `localStorage`
- [ ] BotÃ³n de accesibilidad: incrementar / decrementar tamaÃ±o de fuente
- [ ] TipografÃ­a: cambiar `Inter` por alternativa serif premium (ej. `Playfair Display`)
- [ ] Logo: diseÃ±o minimalista adaptado al sistema Dark Premium
- [ ] Animaciones de entrada para tarjetas y modales (CSS transitions)
- [ ] Notificaciones toast para confirmaciones y errores
- [ ] ConfirmaciÃ³n antes de acciones destructivas (cancelar pedido, etc.)
- [ ] Soporte para teclado en el POS (atajos para operaciones frecuentes)
- [ ] ValidaciÃ³n de formularios con feedback visual en tiempo real

---

## ðŸ—„ï¸ Base de Datos

- [x] Esquema MySQL completo â€” 9 tablas, Ã­ndices, constraints
- [x] Vistas SQL: `v_pedidos_detalle`, `v_productos_inventario`, `v_ventas_empleado`
- [x] Seeds iniciales: 5 cargos, 4 categorÃ­as, 8 mesas, datos de ejemplo
- [x] Ãndices de optimizaciÃ³n: `idx_producto_stock`, `idx_pedido_estado`, `idx_pedido_fecha_desc`
- [ ] Evaluar migrar a `managed=True` en Django para usar migraciones nativas
- [ ] Procedimientos almacenados para cÃ¡lculos de reportes complejos
- [ ] PolÃ­tica de backups automÃ¡ticos (script o tarea programada)
- [ ] Script de seed para datos de prueba en ambiente de desarrollo
- [ ] Documentar el ER diagram (entidad-relaciÃ³n) en `ARCHITECTURE.md`

---

## ðŸ§ª Calidad y Tests

- [ ] Tests unitarios para modelos (`restaurante/tests.py` â€” actualmente vacÃ­o)
- [ ] Tests unitarios para el decorador `@requiere_rol`
- [ ] Tests de integraciÃ³n para `crear_pedido_view` (flujo completo)
- [ ] Tests de API: `api_pedidos_cocina`, `completar_pedido_api`, `pagar_pedido_api`
- [ ] Configurar cobertura de cÃ³digo con `coverage.py` (meta: â‰¥ 80 %)
- [ ] Linting con `flake8` o `ruff` integrado al flujo de desarrollo
- [ ] Formateo automÃ¡tico con `black`

---

## ðŸš€ DevOps / ProducciÃ³n

- [ ] `Makefile` o script `.bat` / `.sh` para arrancar el proyecto en un comando
- [ ] `Dockerfile` para contenedorizar la app Django
- [ ] `docker-compose.yml` con servicios `web` (Django) + `db` (MySQL)
- [ ] Archivo `.env.example` con todas las claves necesarias (sin valores reales)
- [ ] ConfiguraciÃ³n de servidor de producciÃ³n: Gunicorn + Nginx
- [ ] `collectstatic` integrado al proceso de despliegue
- [ ] Pipeline CI/CD bÃ¡sico (GitHub Actions o similar)
- [ ] Monitoreo y alertas de errores en producciÃ³n (ej. Sentry)
- [ ] DocumentaciÃ³n de despliegue paso a paso

---

## ðŸ“– DocumentaciÃ³n

- [x] `README.md` â€” descripciÃ³n, stack, instalaciÃ³n, URLs, convenciones
- [x] `ARCHITECTURE.md` â€” flujo de datos, modelos, patrones, diseÃ±o
- [x] `TASKS.md` â€” este archivo
- [ ] Docstrings en todas las vistas (`views.py`)
- [ ] Docstrings en todos los modelos (`models.py`)
- [ ] `CONTRIBUTING.md` â€” guÃ­a para colaboradores
- [ ] `CHANGELOG.md` â€” historial de cambios por versiÃ³n
- [ ] Diagrama ER en `ARCHITECTURE.md` (generado con dbdiagram.io o similar)

## Deuda de UI / Pulir después (no bloqueante)
- [ ] Copy del KPI dashboard: "críticos" vs "bajo"
- [ ] Reconciliar conteo de alertas dashboard (2) vs inventario (13)
- [ ] Verificar paleta completa de badges de estado
- [ ] Migrar cocina.html a design-system.css
- [x] Normalizar "En preparacion" en BD → resuelto: flujo Pendiente → En Preparación → Listo implementado (14/07/2026)
- [ ] Logo jaguar en sidebar
## Bugs / Arquitectura conocidos
      - [x] BUG crear_pedido.html: el carrito se congela tras el 1er producto.
      Causa: #cart-empty está dentro de #ticket-items; innerHTML lo destruye y
      en el siguiente render getElementById('cart-empty')=null → null.style crashea.
      Fix: renderizar el estado vacío como string dentro de innerHTML, sin mantener
      referencia a un elemento que se destruye.