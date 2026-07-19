# ChefControl Software — Estado del Proyecto

## Stack
Django + MySQL + Materialize CSS → migrando a CSS custom dark premium

## Sesión 14/07/2026 — Flujo cocina Pendiente → En Preparación → Listo
- Nuevo `iniciar_preparacion_api` + guardia en `completar_pedido_api`; ambos con `@requiere_rol('Cocinero','Administrador')` (hueco de seguridad detectado y corregido en la misma sesión).
- `cocina.html`: botón `.btn-iniciar` (naranja) / `.btn-despachar` (verde) según estado, tarjeta y badge "Preparando" tintados, polling sincroniza cambios de otro terminal.
- Pendiente: `api_pedidos_cocina` sigue sin `@requiere_rol` (ver TASKS.md, prioridad media).

## Sesión 18/07/2026 — base.html + toasts de mensajes Django
- Nuevo `templates/base.html` (title/extra_head/content) + sección `.msg-toast*` en `design-system.css`; solo `index.html` migrado a `extends`.
- Resuelve bug: `messages.error` de `requiere_rol` se acumulaba en silencio por falta de `{% if messages %}`. Duración: error/warning 8s, success/info 6s.
- Pendiente: migrar `cocina.html`, `crear_pedido.html`, `facturacion.html`, `login.html` a `base.html` (sesiones futuras, una pantalla a la vez).

## Sesión 19/07/2026 — inventario.html a base.html + fix formulario Materialize
- `inventario.html` migrado a `extends base.html`; eliminado bloque `<style>` de 300 líneas muerto (ninguna clase la usaba el HTML real).
- Causa real de selects/inputs ilegibles: faltaba el `<link>` de `materialize.min.css` (las otras 6 pantallas Materialize sí lo tienen); agregado + `custom-styles.css` ahora cubre `.input-field select` y el dropdown de `M.FormSelect.init()`.
- Pendiente (reportado, no bloqueante): confirm() nativo de "Eliminar" no se puede restylear con CSS, requiere modal propio en sesión aparte.

## Sesión 19/07/2026 (2) — inventario.html reescrito en design-system.css, sin Materialize
- Reescritura completa: sidebar/topbar/stat-card/tabla/status-badge copiados del patrón de `index.html`; selects con `.select-dark` de `crear_pedido.html`; modales propios (overlay+backdrop+panel) reemplazando `M.Modal`; confirm() nativo de Eliminar reemplazado por modal Dark Premium.
- Bug encontrado y corregido: `stock_minimo|divisibleby:2` nunca calculaba "la mitad" (comparaba contra True/False) — reemplazado por `{% widthratio %}`, ahora coincide con la regla real de `views.py`.
- Filtros siguen siendo 100% client-side (confirmado en `inventario_view`, no hay querystring GET); ahora filtran por `data-estado`/`data-categoria` en vez de texto de celdas. `materialize.min.css/js` y `app.js` ya no se cargan en esta pantalla.

