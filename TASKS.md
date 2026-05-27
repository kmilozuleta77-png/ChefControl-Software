# TASKS — ChefControl

Lista de verificación de trabajo organizada por módulo.
Actualiza este archivo al completar o agregar tareas.

- `[x]` Completado
- `[ ]` Pendiente
- `[~]` En progreso / parcial

---

## 🔐 Autenticación y Seguridad

- [x] Login con usuario y contraseña (sistema auth de Django)
- [x] Control de acceso por rol — decorador `@requiere_rol()`
- [x] Protección de vistas con `@login_required`
- [x] `SECRET_KEY` y credenciales de BD en `.env` (nunca en código)
- [x] `DEBUG` condicional según entorno
- [x] Logging estructurado en `logs/chefcontrol.log`
- [x] Errores sanitizados (mensajes genéricos al cliente, detalles en logs)
- [x] Middleware de seguridad Django (CSRF, XFrame, SessionSecurity)
- [ ] Headers de producción activados y verificados (`SECURE_SSL_REDIRECT`, HSTS)
- [ ] Rate limiting en el endpoint de login (protección fuerza bruta)
- [ ] Política de contraseñas (longitud mínima, complejidad)

---

## 🎨 UI Dark Premium

### Pantallas completadas
- [x] `login.html` — Diseño Dark Premium
- [x] `cocina.html` — KDS Dark Premium con polling
- [x] `facturacion.html` — Terminal de caja Dark Premium
- [~] `inventario.html` — Diseño parcial (estructura lista, falta CRUD)

### Pantallas pendientes de rediseño
- [ ] `index.html` — Dashboard: el nuevo diseño no cargó, revisar
- [ ] `crear_pedido.html` — Revisar bug: menús y meseros no cargan desde BD
- [ ] `pedidos.html` — Diseño antiguo, requiere migración
- [ ] `menus.html` — Diseño antiguo + sin conexión a BD
- [ ] `clientes.html` — Sin diseño Dark Premium ni conexión a BD
- [ ] `personal.html` — Sin diseño Dark Premium ni conexión a BD
- [ ] `reportes.html` — Sin diseño Dark Premium ni conexión a BD
- [ ] `configuracion.html` — Sin diseño Dark Premium ni conexión a BD

### Sistema de diseño global
- [ ] Toggle oscuro / claro (sistema de temas global con CSS variables)
- [ ] Botón de accesibilidad (tamaño de fuente dinámico)
- [ ] Cambiar tipografía `Inter` por serif premium en toda la UI
- [ ] Adaptar logo al estilo minimalista Dark Premium
- [ ] Micro-interacciones y animaciones de transición entre vistas
- [ ] Responsive design validado en tablet y móvil

---

## 🏗️ Backend / Lógica de Negocio

### Flujo principal (implementado)
- [x] Crear pedido con `transaction.atomic` (validaciones, detalles)
- [x] API de cocina con polling — `api_pedidos_cocina`
- [x] Marcar pedido como Listo — `completar_pedido_api`
- [x] Registrar pago y emitir factura — `pagar_pedido_api`
- [x] Dashboard con métricas: ventas del día, alertas de stock, pedidos recientes

### CRUD de módulos administrativos (pendiente)
- [ ] **Inventario**: CRUD completo de Productos (crear, editar, desactivar)
- [ ] **Inventario**: ajuste manual de stock (entradas y salidas)
- [ ] **Menús**: CRUD de Categorías y Productos del menú
- [ ] **Clientes**: CRUD completo con búsqueda por cédula / email
- [ ] **Personal**: CRUD de Empleados y Cargos
- [ ] **Reportes**: vistas conectadas a BD usando `v_ventas_empleado`, `v_productos_inventario`
- [ ] **Configuración**: ajustes globales del sistema (nombre del local, IVA, etc.)

### Bugs conocidos
- [ ] `crear_pedido_view`: menús y meseros no cargan desde BD (revisar `GET` context)
- [ ] `dashboard_view`: nuevo diseño Dark Premium no renderiza correctamente

### Mejoras de lógica
- [ ] Propina de monto libre en facturación (actualmente solo porcentaje)
- [ ] Tipos de pedido: implementar lógica para "Para llevar" y "Domicilio"
- [ ] Paginación en historial de pedidos y reportes
- [ ] Búsqueda y filtros en módulo de inventario
- [ ] Exportar reportes a PDF / Excel

---

## 💅 UX / Accesibilidad

- [ ] Toggle modo oscuro / claro global con persistencia en `localStorage`
- [ ] Botón de accesibilidad: incrementar / decrementar tamaño de fuente
- [ ] Tipografía: cambiar `Inter` por alternativa serif premium (ej. `Playfair Display`)
- [ ] Logo: diseño minimalista adaptado al sistema Dark Premium
- [ ] Animaciones de entrada para tarjetas y modales (CSS transitions)
- [ ] Notificaciones toast para confirmaciones y errores
- [ ] Confirmación antes de acciones destructivas (cancelar pedido, etc.)
- [ ] Soporte para teclado en el POS (atajos para operaciones frecuentes)
- [ ] Validación de formularios con feedback visual en tiempo real

---

## 🗄️ Base de Datos

- [x] Esquema MySQL completo — 9 tablas, índices, constraints
- [x] Vistas SQL: `v_pedidos_detalle`, `v_productos_inventario`, `v_ventas_empleado`
- [x] Seeds iniciales: 5 cargos, 4 categorías, 8 mesas, datos de ejemplo
- [x] Índices de optimización: `idx_producto_stock`, `idx_pedido_estado`, `idx_pedido_fecha_desc`
- [ ] Evaluar migrar a `managed=True` en Django para usar migraciones nativas
- [ ] Procedimientos almacenados para cálculos de reportes complejos
- [ ] Política de backups automáticos (script o tarea programada)
- [ ] Script de seed para datos de prueba en ambiente de desarrollo
- [ ] Documentar el ER diagram (entidad-relación) en `ARCHITECTURE.md`

---

## 🧪 Calidad y Tests

- [ ] Tests unitarios para modelos (`restaurante/tests.py` — actualmente vacío)
- [ ] Tests unitarios para el decorador `@requiere_rol`
- [ ] Tests de integración para `crear_pedido_view` (flujo completo)
- [ ] Tests de API: `api_pedidos_cocina`, `completar_pedido_api`, `pagar_pedido_api`
- [ ] Configurar cobertura de código con `coverage.py` (meta: ≥ 80 %)
- [ ] Linting con `flake8` o `ruff` integrado al flujo de desarrollo
- [ ] Formateo automático con `black`

---

## 🚀 DevOps / Producción

- [ ] `Makefile` o script `.bat` / `.sh` para arrancar el proyecto en un comando
- [ ] `Dockerfile` para contenedorizar la app Django
- [ ] `docker-compose.yml` con servicios `web` (Django) + `db` (MySQL)
- [ ] Archivo `.env.example` con todas las claves necesarias (sin valores reales)
- [ ] Configuración de servidor de producción: Gunicorn + Nginx
- [ ] `collectstatic` integrado al proceso de despliegue
- [ ] Pipeline CI/CD básico (GitHub Actions o similar)
- [ ] Monitoreo y alertas de errores en producción (ej. Sentry)
- [ ] Documentación de despliegue paso a paso

---

## 📖 Documentación

- [x] `README.md` — descripción, stack, instalación, URLs, convenciones
- [x] `ARCHITECTURE.md` — flujo de datos, modelos, patrones, diseño
- [x] `TASKS.md` — este archivo
- [ ] Docstrings en todas las vistas (`views.py`)
- [ ] Docstrings en todos los modelos (`models.py`)
- [ ] `CONTRIBUTING.md` — guía para colaboradores
- [ ] `CHANGELOG.md` — historial de cambios por versión
- [ ] Diagrama ER en `ARCHITECTURE.md` (generado con dbdiagram.io o similar)
