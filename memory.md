# ChefControl Software — Estado del Proyecto

## Stack
Django + MySQL + Materialize CSS → migrando a CSS custom dark premium

## Sesión 14/07/2026 — Flujo cocina Pendiente → En Preparación → Listo
- Nuevo `iniciar_preparacion_api` + guardia en `completar_pedido_api`; ambos con `@requiere_rol('Cocinero','Administrador')` (hueco de seguridad detectado y corregido en la misma sesión).
- `cocina.html`: botón `.btn-iniciar` (naranja) / `.btn-despachar` (verde) según estado, tarjeta y badge "Preparando" tintados, polling sincroniza cambios de otro terminal.
- Pendiente: `api_pedidos_cocina` sigue sin `@requiere_rol` (ver TASKS.md, prioridad media).

