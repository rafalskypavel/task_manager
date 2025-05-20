import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()

DEBUG = True
# DEBUG = False
SECRET_KEY = os.getenv('SECRET_KEY')
ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'tasks.apps.TasksConfig',
    'django_filters',
    'django_redis',
    'django_celery_beat',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'task_manager.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'task_manager.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}



# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'


# Локальная временная зона для отображения (форм, админки и т.д.)
TIME_ZONE = os.environ.get("TIME_ZONE", "UTC")

# Указываем, что используем часовые пояса
USE_TZ = True  # Важно! Должно быть True

USE_I18N = True


# Celery configuration
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", 'redis://127.0.0.1:6379/0')
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", 'redis://127.0.0.1:6379/0')
CELERY_TIMEZONE = os.environ.get("CELERY_TIMEZONE", TIME_ZONE)

CELERY_TASK_ACKS_LATE = True  # Подтверждение задач после выполнения
CELERY_WORKER_PREFETCH_MULTIPLIER = 1  # Распределение задач равномерно

CELERY_BEAT_SCHEDULE = {
    'check-deadlines-every-minute': {
        'task': 'tasks.tasks.check_deadlines',
        # 'schedule': crontab(minute='*'),
        'schedule': 30.0,
    },
}

API_URL = os.getenv('API_URL', 'http://localhost:8000/api/')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_TOKEN')

API_REQUEST_TIMEOUT = int(os.getenv('API_REQUEST_TIMEOUT', '10'))

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

# The settings for static files have been updated for the Graded assessment
STATIC_URL = 'tasks/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'tasks', 'static'),
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
