# ChefControl 🍽️

> Sistema de gestión integral para restaurantes — POS, KDS, caja, inventario y administración de personal.

---

## Descripción

**ChefControl** es una aplicación web construida con Django que cubre el ciclo operativo completo de un restaurante:

- **Login con roles** → El personal accede según su cargo (Mesero, Cocinero, Cajero, Administrador).
- **POS** → El mesero crea pedidos con carrito en tiempo real.
- **KDS (Kitchen Display System)** → La cocina recibe y confirma pedidos con polling automático.
- **Terminal de caja** → El cajero factura, aplica descuentos, propinas e impuestos.
- **Inventario** → Gestión de productos con alertas de stock mínimo.
- **Administración** → Módulos de clientes, personal, reportes y configuración (en desarrollo).

---

## Stack

| Capa | Tecnología |
|---|---|
| Backend | Django 6.0.5 · Python 3.x |
| Base de datos | MySQL 8.x |
| ORM | Django ORM (`managed=False`, esquema en MySQL) |
| Frontend | Django Templates + Materialize CSS + CSS Dark Premium |
| JavaScript | Vanilla JS (Materialize init · polling KDS) |
| Variables de entorno | python-dotenv 1.2.2 |

---

## Prerrequisitos

- **Python 3.10+** instalado y en el PATH
- **MySQL 8.x** corriendo en `localhost:3306`
- **pip** actualizado (`pip install --upgrade pip`)
- **Git** (para clonar el repositorio)

---

## Instalación y arranque local

```bash
# 1. Clonar el repositorio
git clone <url-del-repositorio>
cd "ChefControl Software"

# 2. Crear y activar entorno virtual (Windows)
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
#    Copiar el archivo de ejemplo y completar los valores
copy .env.example .env
#    Editar .env con tus credenciales de MySQL (ver sección Variables de entorno)

# 5. Crear la base de datos (primera vez)
mysql -u root -p < chefcontrol_database\chefcontrol_database.sql

# 6. Aplicar migraciones de Django (tablas internas: auth, sessions)
python manage.py migrate

# 7. Crear superusuario para el panel admin (opcional)
python manage.py createsuperuser

# 8. Iniciar el servidor de desarrollo
python manage.py runserver
```

Accede en el navegador:
- **App**: http://localhost:8000
- **Admin Django**: http://localhost:8000/admin

---

## Variables de entorno (`.env`)

```env
DJANGO_SECRET_KEY=<clave-secreta-única-y-larga>
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=chefcontrol_db
DB_USER=root
DB_PASSWORD=<tu-contraseña-mysql>
DB_HOST=127.0.0.1
DB_PORT=3306
```

> ⚠️ **Nunca** subas el archivo `.env` al repositorio. Está incluido en `.gitignore`.

---

## Estructura de URLs

| Ruta | Vista | Descripción |
|---|---|---|
| `/` | `login_view` | Inicio de sesión |
| `/dashboard/` | `dashboard_view` | Panel principal con métricas |
| `/nuevo-pedido/` | `crear_pedido_view` | POS: crear pedido (mesero) |
| `/cocina/` | `cocina_view` | KDS: pantalla de cocina |
| `/facturacion/` | `facturacion_view` | Terminal de caja |
| `/inventario/` | `inventario_view` | Gestión de productos |
| `/logout/` | `logout_view` | Cierre de sesión |
| `/admin/` | Django Admin | Administración interna |
| `/api/pedidos-cocina/` | `api_pedidos_cocina` | API JSON: pedidos pendientes |
| `/pedido/<id>/completar/` | `completar_pedido_api` | API: marcar pedido Listo |
| `/pedido/<id>/pagar/` | `pagar_pedido_api` | API: registrar pago |

---

## Comandos útiles de Django

```bash
python manage.py runserver          # Servidor de desarrollo
python manage.py migrate            # Aplicar migraciones
python manage.py makemigrations     # Generar nuevas migraciones
python manage.py createsuperuser    # Crear admin
python manage.py shell              # Shell interactivo Django
python manage.py dbshell            # Shell de MySQL
python manage.py collectstatic      # Recolectar estáticos (producción)
```

---

## Convenciones de desarrollo

- **Git**: nunca tocar `master`/`main`; cada feature en su propia rama descriptiva.
- **Calidad**: Clean Code, principios SOLID, todos los comentarios en español.
- **UX**: diseño Dark Premium con Materialize CSS; cero layouts genéricos.
- **Seguridad**: validación siempre en backend, variables sensibles en `.env`.

---

## Licencia

Proyecto privado — todos los derechos reservados.
