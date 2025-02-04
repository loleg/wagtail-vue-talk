"""Overwrite settings with production settings when going live."""
from .settings_base import *

import os
import dj_database_url

# Do not set SECRET_KEY, Postgres or LDAP password or any other sensitive data here.
# Instead, use environment variables or create a local.py file on the server.

# Disable debug mode
DEBUG = False
TEMPLATES[0]['OPTIONS']['debug'] = False

# Configuration from environment variables
# Alternatively, you can set these in a local.py file on the server

env = os.environ.copy()


# Basic configuration

APP_NAME = env.get('APP_NAME', 'wagtailvue')

if 'SECRET_KEY' in env:
    SECRET_KEY = env['SECRET_KEY']

if 'ALLOWED_HOSTS' in env:
    ALLOWED_HOSTS = env['ALLOWED_HOSTS'].split(',')

if 'PRIMARY_HOST' in env:
    BASE_URL = 'http://%s/' % env['PRIMARY_HOST']

if 'SERVER_EMAIL' in env:
    SERVER_EMAIL = env['SERVER_EMAIL']

if 'CACHE_PURGE_URL' in env:
    INSTALLED_APPS += ( 'wagtail.contrib.frontend_cache', )
    WAGTAILFRONTENDCACHE = {
        'default': {
            'BACKEND': 'wagtail.contrib.frontend_cache.backends.HTTPBackend',
            'LOCATION': env['CACHE_PURGE_URL'],
        },
    }

if 'STATIC_URL' in env:
    STATIC_URL = env['STATIC_URL']

if 'STATIC_DIR' in env:
    STATIC_ROOT = env['STATIC_DIR']

if 'MEDIA_URL' in env:
    MEDIA_URL = env['MEDIA_URL']

if 'MEDIA_DIR' in env:
    MEDIA_ROOT = env['MEDIA_DIR']


# Database

if 'DATABASE_URL' in os.environ:
    DATABASES = {'default': dj_database_url.config()}

else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': env.get('PGDATABASE', APP_NAME),
            'CONN_MAX_AGE': 600,  # number of seconds database connections should persist for

            # User, host and port can be configured by the PGUSER, PGHOST and
            # PGPORT environment variables (these get picked up by libpq).
        }
    }


# Email via ESP

if 'MAILGUN_KEY' in os.environ:
    EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"
    ANYMAIL = {
        "MAILGUN_API_KEY": env['MAILGUN_KEY'],
        "MAILGUN_SENDER_DOMAIN": env['MAILGUN_DOMAIN']
    }
    DEFAULT_FROM_EMAIL = env['MAILGUN_FROM']

# Redis location can either be passed through with REDIS_HOST or REDIS_SOCKET

if 'REDIS_URL' in env:
    REDIS_LOCATION = env['REDIS_URL']
    BROKER_URL = env['REDIS_URL']

elif 'REDIS_HOST' in env:
    REDIS_LOCATION = env['REDIS_HOST']
    BROKER_URL = 'redis://%s' % env['REDIS_HOST']

elif 'REDIS_SOCKET' in env:
    REDIS_LOCATION = 'unix://%s' % env['REDIS_SOCKET']
    BROKER_URL = 'redis+socket://%s' % env['REDIS_SOCKET']

else:
    REDIS_LOCATION = None

if REDIS_LOCATION is not None:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_LOCATION,
            'KEY_PREFIX': APP_NAME,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }

# Use Elasticsearch as the search backend for extra performance and better search results

if 'ELASTICSEARCH_URL' in env:
    WAGTAILSEARCH_BACKENDS = {
        'default': {
            'BACKEND': 'wagtail.search.backends.elasticsearch5',
            'URLS': [env['ELASTICSEARCH_URL']],
            'INDEX': APP_NAME,
            'ATOMIC_REBUILD': True,
        },
    }

if 'LOG_DIR' in env:
    # Wagtail log
    LOGGING['handlers']['wagtail_file'] = {
        'level':        'WARNING',
        'class':        'concurrent_log_handler.ConcurrentRotatingFileHandler',
        'filename':     os.path.join(env['LOG_DIR'], 'wagtail.log'),
        'maxBytes':     5242880, # 5MB
        'backupCount':  5
    }
    LOGGING['loggers']['wagtail']['handlers'].append('wagtail_file')

    # Error log
    LOGGING['handlers']['errors_file'] = {
        'level':        'ERROR',
        'class':        'concurrent_log_handler.ConcurrentRotatingFileHandler',
        'filename':     os.path.join(env['LOG_DIR'], 'error.log'),
        'maxBytes':     5242880, # 5MB
        'backupCount':  5
    }
    LOGGING['loggers']['django.request']['handlers'].append('errors_file')
    LOGGING['loggers']['django.security']['handlers'].append('errors_file')

try:
    from .local import *
except ImportError:
    pass
