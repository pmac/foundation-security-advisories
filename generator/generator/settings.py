import os

from decouple import config


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


SECRET_KEY = 'do not run this site in production. it is a static generator.'

DEBUG = config('DEBUG', True, cast=bool)

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = (
    'django.contrib.staticfiles',
    'django_jinja',
    'django_jinja_markdown',
    'generator.security',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
)

ROOT_URLCONF = 'generator.urls'

TEMPLATES = [
    {
        'BACKEND': 'django_jinja.backend.Jinja2',
        'APP_DIRS': True,
        'OPTIONS': {
            'match_extension': None,
            'undefined': 'jinja2.Undefined',
            'finalize': lambda x: x if x is not None else '',
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.media',
                'django.template.context_processors.request',
                'generator.security.context_processors.current_year'
            ],
            'extensions': [
                'jinja2.ext.do',
                'jinja2.ext.with_',
                'jinja2.ext.loopcontrols',
                'jinja2.ext.autoescape',
                'jinja2.ext.i18n',
                'django_jinja.builtins.extensions.StaticFilesExtension',
                'django_jinja.builtins.extensions.DjangoFiltersExtension',
                'django_jinja.builtins.extensions.UrlsExtension',
                'django_jinja_markdown.extensions.MarkdownExtension',
            ],
        }
    },
]

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        # 'NAME': ':memory:',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

TIME_ZONE = 'UTC'
USE_TZ = True
USE_I18N = False
USE_L10N = False

STATIC_URL = '/static/'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

ADVISORIES_PATH = os.path.dirname(BASE_DIR)
SITE_OUTPUT_PATH = os.path.join(ADVISORIES_PATH, '_publish')
STATIC_ROOT = os.path.join(SITE_OUTPUT_PATH, 'static')
