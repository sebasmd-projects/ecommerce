from unipath import Path

from app_core_bookface.get_value_from_json import obtener_valor

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).ancestor(3)

# Seleccionar el entorno de trabajo
environment = f"{obtener_valor('ENVIRONMENT')}"


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = obtener_valor('SECRET_KEY')

# Trabajar con otro modelo para el usuario
AUTH_USER_MODEL = 'authentication.ModeloPersonas'

# URL Global
BASE_URL = obtener_valor('BASE_URL')

# SECURITY WARNING: don't run with debug turned on in production!
if environment == 'prod':
    DEBUG = False
else:
    DEBUG = True


# Redirigir a SSL si es necesario (Producción)
if environment == 'prod':
    SECURE_SSL_REDIRECT = True
else:
    SECURE_SSL_REDIRECT = False
    
# urls permitidas
ALLOWED_HOSTS = obtener_valor('ALLOWED_HOSTS')[environment]

# Cors permitidos
CORS_ALLOWED_ORIGINS = obtener_valor('CORS_ALLOWED_ORIGINS')[environment]


# Apps de Django
DJANGO_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

# Apps de terceros
THIRD_PARTY_APPS = (
    'rest_framework',
    'corsheaders',
    'import_export',
)

# Apps locales
LOCAL_APPS = (
    'apps.authentication',
)

# Unir apps de terceros, locales y de Django
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'app_core_bookface.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR.child('public', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.context_processors.custom_processors',
            ],
        },
    },
]

WSGI_APPLICATION = 'app_core_bookface.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'CONN_MAX_AGE': obtener_valor('DB_CONN_MAX_AGE'),
        'ENGINE': obtener_valor('DB_ENGINE'),
        'NAME': obtener_valor('DB_NAME'),
        'USER': obtener_valor('DB_USER'),
        'PASSWORD': obtener_valor('DB_PASSWORD'),
        'HOST': obtener_valor('DB_HOST'),
        'PORT': obtener_valor('DB_PORT')
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = obtener_valor('LANGUAGE_CODE')

TIME_ZONE = obtener_valor('TIME_ZONE')

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = ['public/static',]

MEDIA_URL = '/media/'
MEDIA_ROOT = 'public/media/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Configuración de correo
if bool(obtener_valor('EMAIL_USE_TLS')) == True:
    EMAIL_USE_TLS = True
else:
    EMAIL_USE_SSL = True
EMAIL_HOST = obtener_valor('EMAIL_HOST')
EMAIL_PORT = obtener_valor('EMAIL_PORT')
EMAIL_HOST_USER = obtener_valor('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = obtener_valor('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER