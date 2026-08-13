# TASKS â€” ChefControl

Lista de verificaciÃ³n de trabajo organizada por mÃ³dulo.
Actualiza este archivo al completar o agregar tareas.

- `[x]` Completado
- `[ ]` Pendiente
- `[~]` En progreso / parcial

---

## ðŸ” AutenticaciÃ³n y Seguridad

- [ ] Headers de producciÃ³n activados y verificados (`SECURE_SSL_REDIRECT`, HSTS)
- [ ] Rate limiting en el endpoint de login (protecciÃ³n fuerza bruta)
- [ ] PolÃ­tica de contraseÃ±as (longitud mÃ­nima, complejidad)
 

---



### Pantallas pendientes de rediseño
- [x] `pedidos.html` — Migrado a Dark Premium + `pedidos_view` (filtro estado/período, paginación) + URL `name='pedidos'`; sidebar y "Ver todos" del dashboard ya enlazan aquí
- [ ] `configuracion.html` — Sin diseño Dark Premium ni conexión a BD

### Sistema de diseÃ±o global
- [ ] Cambiar tipografÃ­a `Inter` por serif premium en toda la UI
- [ ] Adaptar logo al estilo minimalista Dark Premium
- [ ] Micro-interacciones y animaciones de transiciÃ³n entre vistas
- [ ] Responsive design validado en tablet y mÃ³vil

---

## ðŸ—ï¸ Backend / LÃ³gica de Negocio

### CRUD de mÃ³dulos administrativos (pendiente)



- [~] **Personal**: CRUD completo de Empleados con soft-delete (estado='Inactivo', fk_pedido_empleado y fk_factura_empleado son ON DELETE RESTRICT) (19/07/2026); falta CRUD de Cargos
- [ ] **Configuración**: ajustes globales del sistema (nombre del local, IVA, etc.)
- [ ] `v_ventas_empleado` no tiene columna de fecha — no se usa en Reportes (que sí filtra por período); candidata a rediseño futuro si se quiere usar ahí

### Bugs conocidos
- [ ] Evaluar mover `<script>` de index.html al final de `</body>` o usar `defer` (evita el patrón de orden para todo el archivo, no urgente)
- [ ] **Deuda técnica menor**: cambiar `fecha_pedido` a `auto_now_add=True` en modelo `Pedido` para garantizar que nunca quede NULL sin depender de la vista
- [ ] **Deuda tecnica**: ampliar `Factura.metodo_pago` a `max_length=30` con migracion — coordinar con Sofia; hoy `'Tarjeta Credito'` ocupa 14 chars, cabe justo; riesgo si se agregan metodos mas largos
- [ ] **Deuda tecnica**: centralizar codigos de metodo de pago en constante JS compartida en `facturacion.html` — hoy el literal `'efectivo'` esta disperso en `calcularCambio()`, `abrirModal()` y `confirmarPago()`
- [ ] **Deuda tecnica**: convertir `Factura.estado` a campo `choices` — hoy `CharField(9)` libre; `'Pagada'` cabe justo, cualquier estado mas largo (ej. `'Pendiente'`) agota el limite
- [ ] **Deuda tecnica (pendiente hasta terminar Clientes/Empleados)**: extraer a `design-system.css` el bloque CSS de modales (`.modal-overlay`, `.modal-panel`, `.form-grid`, `.field-input`, etc.) duplicado igual en `index.html`, `inventario.html` y `clientes.html`
- [ ] **Deuda tecnica (pendiente hasta terminar Clientes/Empleados)**: extraer a un JS compartido el bloque de tema oscuro/claro, tamaño de fuente, reloj en vivo y toggle de sidebar, duplicado igual en `index.html`, `inventario.html` y `clientes.html`
- [ ] **Bug**: `dashboard_view` (views.py:107) filtra `Empleado.objects.filter(estado='Descanso')` pero el ENUM real en MySQL es `('Activo','Inactivo')` — "Descanso" no existe, el conteo `empleados_descanso` siempre da 0. Detectado durante diagnóstico de CRUD Empleado (19/07/2026), fuera de alcance de esa sesión (pantalla dashboard, no personal)
- [ ] **Deuda técnica**: sidebar "Pedidos" (dashboard, reportes, pedidos, clientes, inventario, personal) quedó sin badge de conteo — antes mostraba un `4` hardcodeado sin fuente real de datos. Un badge de "pedidos pendientes" real requiere un context processor que calcule el conteo en cada request (no una query repetida por vista); pendiente para sesión futura

### Mejoras de lÃ³gica
- [ ] Propina de monto libre en facturaciÃ³n (actualmente solo porcentaje)
- [ ] Tipos de pedido: implementar lÃ³gica para "Para llevar" y "Domicilio"
- [ ] PaginaciÃ³n en historial de pedidos y reportes
- [ ] BÃºsqueda y filtros en mÃ³dulo de inventario
- [ ] Exportar reportes a PDF / Excel
- [ ] Rediseño de flujo de Factura: hoy la Factura se crea recién al
  pagar (pagar_pedido_api), sin estado intermedio. Idea propuesta:
  emitir la Factura como 'Pendiente' cuando se pide la cuenta (antes
  de pagar), permitiendo imprimir/mostrar tirilla al cliente antes del
  cobro, con estados reales (Pendiente, Pagada, Pago Parcial, Vencida).
  Requiere separar creación de Factura del momento de pago, y decidir
  si aplican todos esos estados a un restaurante o es más propio de
  facturación a crédito. Rediseño de flujo, no ajuste puntual.

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

## ðŸ—„ï¸ Base de Datos

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
- [ ] Logo jaguar en sidebar
