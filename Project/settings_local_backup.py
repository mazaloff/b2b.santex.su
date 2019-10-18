import os

EMAIL_HOST_PASSWORD = 'Gjkmpf314159'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'websitedb',
        'USER': 'sa',
        'PASSWORD': '123',
        'HOST': '192.168.115.3',
        'PORT': '5432',
        'CONN_MAX_AGE': 60 * 10,  # 10 minutes
    }
}

CELERY_NO_CREATE_ORDERS = True

ALLOWED_HOSTS = ['127.0.0.1', '185.46.154.84', '127.0.0.1:9001']
API_URL = 'http://localhost:8000/STBase/hs/'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PYTHON_BIN = r"C:\Users\LenovoMaz\.virtualenvs\Project-dOAYzJCZ\Scripts"
PYTHON_EXE = r"C:\Users\LenovoMaz\.virtualenvs\Project-dOAYzJCZ\Scripts\python.exe"

SERVER_ARI = ('127.0.0.1', 8081)
SERVER_NGINX = ('127.0.0.1', 8080)
URL = 'http://127.0.0.1:9001'

DEBUG = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
        }
    },
}

# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'filters': {
#         'require_debug_false': {
#             '()': 'django.utils.log.RequireDebugFalse'
#         }
#     },
#     'handlers': {
#         'console': {
#             'class': 'logging.StreamHandler',
#         },
#     },
#     'loggers': {
#         'django.request': {
#             'handlers': ['console'],
#             'level': 'ERROR',
#             'propagate': True,
#         },
#     }
# }
