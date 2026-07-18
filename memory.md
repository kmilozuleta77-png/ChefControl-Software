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

