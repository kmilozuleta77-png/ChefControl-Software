# ChefControl Software — Estado del Proyecto

## Stack
Django + MySQL + Materialize CSS → migrando a CSS custom dark premium

## Rama activa
feature/ui-dark-premium

## Completado ✅
- Seguridad: .env, SECRET_KEY, DEBUG condicional, LOGGING
- Arquitectura: roles, validación backend, errores sanitizados
- UI Dark Premium: login, cocina, facturación, inventario (parcial)

## Pendiente 🔧
- Dashboard: no cargó el nuevo diseño, revisar
- Toggle modo oscuro/claro global
- Botón accesibilidad (tamaño fuente)
- Propina libre en facturación (no solo porcentaje)
- Pantalla pedidos: menús y mesero no cargan desde DB
- Tipografía: cambiar Inter por serif premium
- Logo: adaptar al estilo minimalista
- Pantallas nuevas: menús, clientes, personal, reportes, configuración

## Próxima sesión
1. Corregir dashboard
2. Implementar toggle oscuro/claro
3. Revisar pantalla pedidos con DB real