"""
Configuración principal de ChefControl Software.
Las variables sensibles se leen desde el archivo .env (nunca versionar credenciales).
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Cargamos las variables del archivo .env
load_dotenv(BASE_DIR / '.env')

# ---------------------------------------------------------------
# SEGURIDAD
# ---------------------------------------------------------------

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("DJANGO_SECRET_KEY no está definida en el archivo .env")

DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = [h.strip() for h in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')]

# ---------------------------------------------------------------
# APLICACIONES INSTALADAS
# ---------------------------------------------------------------

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'restaurante',
]

# ---------------------------------------------------------------
# MIDDLEWARE
# ---------------------------------------------------------------

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'chefcontrol_backend.urls'

# ---------------------------------------------------------------
# TEMPLATES
# ---------------------------------------------------------------

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'chefcontrol_backend.wsgi.application'

# ---------------------------------------------------------------
# BASE DE DATOS
# ---------------------------------------------------------------

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',

        'NAME': 'chefcontrol_db',
        'USER': 'root', 
        'PASSWORD': '8902',
        'HOST': '127.0.0.1',
        'PORT': '3306',

        'NAME': os.getenv('DB_NAME', 'chefcontrol_db'),
        'USER': os.getenv('DB_USER', 'root'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('DB_PORT', '3306'),

    }
}

# ---------------------------------------------------------------
# VALIDACIÓN DE CONTRASEÑAS
# ---------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ---------------------------------------------------------------
# INTERNACIONALIZACIÓN
# ---------------------------------------------------------------

LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------
# ARCHIVOS ESTÁTICOS
# ---------------------------------------------------------------

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ---------------------------------------------------------------
# LOGGING — Registra advertencias y errores en archivo
# ---------------------------------------------------------------

LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detallado': {
            'format': '[{levelname}] {asctime} {module} — {message}',
            'style': '{',
        },
    },
    'handlers': {
        'archivo': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'chefcontrol.log',
            'formatter': 'detallado',
            'encoding': 'utf-8',
        },
        'consola': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'detallado',
        },
    },
    'loggers': {
        'restaurante': {
            'handlers': ['archivo', 'consola'],
            'level': 'DEBUG' if DEBUG else 'WARNING',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['archivo'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# ---------------------------------------------------------------
# HEADERS DE SEGURIDAD (solo en producción, cuando DEBUG=False)
# ---------------------------------------------------------------

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000          # 1 año
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'