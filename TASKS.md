# TASKS — ChefControl

Lista de verificación de trabajo organizada por módulo.
Actualiza este archivo al completar o agregar tareas.

- `[x]` Completado
- `[ ]` Pendiente
- `[~]` En progreso / parcial

---

## 🔐 Autenticación y Seguridad

- [ ] Headers de producción activados y verificados (`SECURE_SSL_REDIRECT`, HSTS) — ya configurado en settings.py para producción (Render), verificar que estén realmente activos en el entorno desplegado
- [ ] Rate limiting en el endpoint de login (protección fuerza bruta)
- [ ] Política de contraseñas (longitud mínima, complejidad)

---

## 🎨 UI Dark Premium

### Pantallas pendientes de rediseño
- [ ] `configuracion.html` — Sin diseño Dark Premium ni conexión a BD (fuera de alcance de la entrega EV02, próxima iteración)

### Sistema de diseño global
- [ ] Cambiar tipografía `Inter` por serif premium en toda la UI
- [ ] Adaptar logo al estilo minimalista Dark Premium
- [ ] Micro-interacciones y animaciones de transición entre vistas
- [ ] Responsive design validado en tablet y móvil

---

## 🏗️ Backend / Lógica de Negocio

### CRUD de módulos administrativos (pendiente)
- [ ] Configuración — sección Mi Cuenta
- [ ] Configuración — sección Notificaciones
- [ ] Configuración — sección Seguridad
- [ ] Configuración — sección Sistema
- [ ] `v_ventas_empleado` no tiene columna de fecha — no se usa en Reportes (que sí filtra por período); candidata a rediseño futuro si se quiere usar ahí

### Bugs conocidos
- [ ] Evaluar mover `<script>` de index.html al final de `</body>` o usar `defer` (evita el patrón de orden para todo el archivo, no urgente)
- [ ] **Deuda técnica menor**: cambiar `fecha_pedido` a `auto_now_add=True` en modelo `Pedido` para garantizar que nunca quede NULL sin depender de la vista
- [ ] **Deuda técnica**: ampliar `Factura.metodo_pago` a `max_length=30` con migración — coordinar con Sofía; hoy `'Tarjeta Crédito'` ocupa 14 chars, cabe justo; riesgo si se agregan métodos más largos
- [ ] **Deuda técnica**: centralizar códigos de método de pago en constante JS compartida en `facturacion.html` — hoy el literal `'efectivo'` está disperso en `calcularCambio()`, `abrirModal()` y `confirmarPago()`
- [ ] **Deuda técnica**: convertir `Factura.estado` a campo `choices` — hoy `CharField(9)` libre; `'Pagada'` cabe justo, cualquier estado más largo (ej. `'Pendiente'`) agota el límite
- [ ] **Deuda técnica**: extraer a `design-system.css` el bloque CSS de modales (`.modal-overlay`, `.modal-panel`, `.form-grid`, `.field-input`, `.categoria-lista`, `.categoria-item`, etc.) duplicado en `index.html`, `inventario.html`, `personal.html` y `clientes.html`
- [ ] **Deuda técnica**: extraer a un JS compartido el bloque de tema oscuro/claro, tamaño de fuente, reloj en vivo y toggle de sidebar, duplicado en todos los templates con sidebar
- [ ] **Deuda técnica**: el bloque de sidebar completo se repite en 6+ templates — evaluar `{% include 'partials/sidebar.html' %}` para no tener que corregir un link roto en 6 archivos a la vez
- [ ] **Bug**: `dashboard_view` filtra `Empleado.objects.filter(estado='Descanso')` pero el ENUM real en MySQL es `('Activo','Inactivo')` — "Descanso" no existe, el conteo `empleados_descanso` siempre da 0
- [ ] **Deuda técnica**: sidebar "Pedidos" quedó sin badge de conteo real (antes mostraba un `4` hardcodeado). Un badge de "pedidos pendientes" real requiere un context processor que calcule el conteo en cada request

### Mejoras de lógica
- [ ] Propina de monto libre en facturación (actualmente solo porcentaje)
- [ ] Tipos de pedido: implementar lógica para "Para llevar" y "Domicilio"
- [ ] Búsqueda y filtros en módulo de inventario
- [ ] Exportar reportes a PDF / Excel
- [ ] **Factura: formato de impresión** — implementar dos formatos de salida: tirilla (POS, ancho angosto) y tamaño carta (documento formal), según el tipo de comprobante (`tipo_comprobante` ya existe en `pagar_pedido_api`: 'pos' vs 'fe')
- [ ] Rediseño de flujo de Factura: hoy la Factura se crea recién al
  pagar (pagar_pedido_api), sin estado intermedio. Idea propuesta:
  emitir la Factura como 'Pendiente' cuando se pide la cuenta (antes
  de pagar), permitiendo imprimir/mostrar tirilla al cliente antes del
  cobro, con estados reales (Pendiente, Pagada, Pago Parcial, Vencida).
  Requiere separar creación de Factura del momento de pago, y decidir
  si aplican todos esos estados a un restaurante o es más propio de
  facturación a crédito. Rediseño de flujo, no ajuste puntual.

---

## 💅 UX / Accesibilidad

- [ ] **Bug: tema oscuro/claro no persiste al navegar a "Nuevo Pedido" o "Cocina"** — el toggle sí guarda en localStorage y funciona en el resto de pantallas, pero `crear_pedido.html` y `cocina.html` no están aplicando el tema guardado al cargar (posible causa: son de los templates más viejos, capturado antes de que el bloque de tema se estandarizara en el resto de pantallas)
- [ ] **Bug responsive: `crear_pedido.html` en móvil** — un `div` ocupa demasiado espacio vertical y tapa el campo de observaciones y el botón "Enviar Orden" en pantallas de celular
- [ ] Botón de accesibilidad: incrementar / decrementar tamaño de fuente (verificar que funcione igual en todas las pantallas)
- [ ] Tipografía: cambiar `Inter` por alternativa serif premium (ej. `Playfair Display`)
- [ ] Logo: diseño minimalista adaptado al sistema Dark Premium
- [ ] Animaciones de entrada para tarjetas y modales (CSS transitions)
- [ ] Confirmación antes de acciones destructivas (cancelar pedido, etc.)
- [ ] Soporte para teclado en el POS (atajos para operaciones frecuentes)
- [ ] Validación de formularios con feedback visual en tiempo real

---

## 🗄️ Base de Datos

- [ ] Evaluar migrar a `managed=True` en Django para usar migraciones nativas
- [ ] Procedimientos almacenados para cálculos de reportes complejos
- [ ] Política de backups automáticos (script o tarea programada) — considerar el backup automático que ofrece Aiven en planes pagos
- [ ] Documentar el ER diagram (entidad-relación) en `ARCHITECTURE.md`

---

## 🚀 DevOps / Producción

- [ ] Documentación de despliegue paso a paso para la EV02 (arquitectura Render + Aiven, variables de entorno, Secret File del certificado SSL)

---

## 📖 Documentación

- [ ] Docstrings en todas las vistas (`views.py`)
- [ ] Docstrings en todos los modelos (`models.py`)
- [ ] `CONTRIBUTING.md` — guía para colaboradores
- [ ] `CHANGELOG.md` — historial de cambios por versión
- [ ] Diagrama ER en `ARCHITECTURE.md` (generado con dbdiagram.io o similar)
- [ ] Diagrama de despliegue (arquitectura física: Render + Aiven + navegador cliente) para la entrega EV02

---

## Deuda de UI / Pulir después (no bloqueante)

- [ ] Copy del KPI dashboard: "críticos" vs "bajo"
- [ ] Reconciliar conteo de alertas dashboard vs inventario
- [ ] Verificar paleta completa de badges de estado
- [ ] Migrar cocina.html a design-system.css
- [ ] Logo jaguar en sidebar
- [ ] Inconsistencia de `class="active"` en el link activo del sidebar — `clientes.html` lo usa en su propio ítem, pero `inventario.html`/`personal.html` no siguen el mismo patrón para el suyo