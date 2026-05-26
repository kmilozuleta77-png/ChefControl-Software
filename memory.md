## Estado actual — 26/05/2026
- Rama: feature/reestructuracion-completa (4 commits)
- Fase 1 ✅: .env, settings.py seguro, requirements.txt, LOGGING
- Fase 2 ✅: models.py con índices y PROTECT en FKs
- Fase 3 ✅: views.py con roles, validación backend, errores sanitizados
- Fase 4 ✅: cocina.html con fetch polling, onclick inline eliminados

## Pendiente
- Rate limiting en login
- Content Security Policy

## Estado 26/05/2026
- Reestructuración completa: seguridad, arquitectura, bugs corregidos ✅
- Próxima fase: Rediseño UI Dark Premium

### Sistema de diseño Dark Premium
- Fondo base: #0a0a0a
- Cards: #111111, bordes: #1f1f1f
- Color principal: naranja #f97316 | Hover: #ea580c
- Texto primario: #f5f5f5, secundario: #737373
- Tipografía: Inter (Google Fonts)
- border-radius: 12px cards, 8px botones
- Inputs con borde inferior solamente
- Sidebar oscuro con íconos Material Icons

### Funcionalidades globales requeridas
1. Toggle modo oscuro/claro en el header
2. Botón de accesibilidad (aumentar/reducir tamaño de fuente)
3. Reorganización moderna de botones y navegación

### Orden de trabajo (un commit por pantalla)
1. login → 2. dashboard → 3. crear_pedido → 4. cocina → 5. facturacion → 6. inventario

### Protocolo antes de cada pantalla
- Proponer sugerencias UX/UI adicionales no mencionadas por el usuario
- Explicar en español qué se va a cambiar y por qué