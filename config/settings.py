import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ── Helper pour lire les variables d'environnement ────────────
def env(key, default=''):
    return os.environ.get(key, default)

def env_bool(key, default=False):
    return os.environ.get(key, str(default)).lower() in ('true', '1', 'yes')

# ── Paramètres de base ────────────────────────────────────────
SECRET_KEY = env('SECRET_KEY', 'dev-secret-key-change-in-prod')
DEBUG = env_bool('DEBUG', True)
ALLOWED_HOSTS = env('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.users',
    'apps.dossiers',
    'apps.dashboard',
    'apps.audit',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.audit.middleware.AuditMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME', 'sgd_db'),
        'USER': env('DB_USER', 'sgd_user'),
        'PASSWORD': env('DB_PASSWORD', 'changeme'),
        'HOST': env('DB_HOST', 'db'),
        'PORT': env('DB_PORT', '5432'),
    }
}

AUTH_USER_MODEL = 'users.User'
LOGIN_URL = '/users/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/users/login/'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Porto-Novo'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'mediafiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.db'

WAZUH_API_URL          = env('WAZUH_API_URL',          'https://wazuh-manager:55000')
WAZUH_INDEXER_URL      = env('WAZUH_INDEXER_URL',      'https://wazuh-indexer:9200')
WAZUH_API_USER         = env('WAZUH_API_USER',         'wazuh-wui')
WAZUH_API_PASSWORD     = env('WAZUH_API_PASSWORD',     'changeme')
WAZUH_INDEXER_USER     = env('WAZUH_INDEXER_USER',     'admin')
WAZUH_INDEXER_PASSWORD = env('WAZUH_INDEXER_PASSWORD', 'changeme')
THEHIVE_URL        = env('THEHIVE_URL',        'http://localhost:9000')
THEHIVE_API_KEY    = env('THEHIVE_API_KEY',    '')
OPENPROJECT_URL    = env('OPENPROJECT_URL',    'http://localhost:8081')
OPENPROJECT_API_KEY= env('OPENPROJECT_API_KEY','')

if not DEBUG:
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
