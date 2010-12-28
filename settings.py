# -*- coding: utf-8 -*-
# Django tintzsettings for social pinax project.

import os.path
import posixpath
import pinax

PINAX_ROOT = os.path.abspath(os.path.dirname(pinax.__file__))
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# tells Pinax to use the default theme
PINAX_THEME = 'default'

# Sphinx 0.9.8

#SMTP Server #TODO: change email
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'daniel.franca@gmail.com'
EMAIL_HOST_PASSWORD = '_739d07CFNt!@8399'
EMAIL_SUBJECT_PREFIX = 'Tintz - '
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'daniel.franca@gmail.com'
EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'
EMAIL_FILE_PATH = os.path.join(os.path.dirname(__file__),'emaildata')

DEBUG = True
TEMPLATE_DEBUG = DEBUG

# tells Pinax to serve media through django.views.static.serve.
SERVE_MEDIA = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'postgresql_psycopg2'    # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_NAME = 'tintz_dev'       # Or path to database file if using sqlite3.
DATABASE_USER = 'tintz'             # Not used with sqlite3.
DATABASE_PASSWORD = 'visio@123!'         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
# although not all variations may be possible on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Sao_Paulo'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'pt-br'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'site_media')
#MEDIA_ROOT = os.path.join(os.path.dirname(__file__), "site_media")



# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = '/site_media/'

# Absolute path to the directory that holds static files like app media.
# Example: "/home/media/media.lawrence.com/apps/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'site_media', 'static')

# URL that handles the static files like app media.
# Example: "http://media.lawrence.com"
STATIC_URL = '/site_media/static/'

# Dajax
DAJAXICE_MEDIA_PREFIX="dajaxice"
DAJAX_JS_FRAMEWORK = "jQuery"
DAJAXICE_DEBUG = True

# Additional directories which hold static files
STATICFILES_DIRS = (
    ('tintz', os.path.join(PROJECT_ROOT, 'media')),
    ('pinax', os.path.join(PINAX_ROOT, 'media', PINAX_THEME)),
)

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = posixpath.join(STATIC_URL, "admin/")

# Make this unique, and don't share it with anybody.
SECRET_KEY = '-uj77g9(u7ov598ek!&%!n-lfh_&&$974=mv-jqc9$v209r1dp'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
    'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'django_openid.consumer.SessionConsumer',
    'account.middleware.LocaleMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'pagination.middleware.PaginationMiddleware',
    #'django_sorting.middleware.SortingMiddleware',
    #'djangodblog.middleware.DBLogMiddleware',
    'pinax.middleware.security.HideSensistiveFieldsMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
)

ROOT_URLCONF = 'tintz.urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, "templates"),
    #os.path.join(PINAX_ROOT, "templates", PINAX_THEME),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",

    "pinax.core.context_processors.pinax_settings",

    #"notification.context_processors.notification",
    "announcements.context_processors.site_wide_announcements",
    "account.context_processors.account",
    "messages.context_processors.inbox",
    "tintz.context_processors.combined_inbox_count",
)

COMBINED_INBOX_COUNT_SOURCES = (
    "messages.context_processors.inbox",
    #"notification.context_processors.notification",
)

INSTALLED_APPS = (
    # included
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.humanize',
    'django.contrib.markup',
    'pinax.templatetags',

    # external
    #'notification', # must be first
    'emailconfirmation',
    'django_extensions',
    'robots',
    'mailer',
    'messages',
    'announcements',
    'pagination',
    'threadedcomments',
    'threadedcomments_extras',
    'timezones',
    'tagging',
    'blog',
    'ajax_validation',
    'avatar',
    'uni_form',
    'haystack',

    # internal (for now)
    'profiles',
    'account',
    'tag_app',

    #mine
    'publications',
    'tintzsettings',
    'follow',
    #'pagseguropy',

    #Ajax
    'dajaxice',
    'dajax',

    'django.contrib.admin',

)

ABSOLUTE_URL_OVERRIDES = {
    "auth.user": lambda o: "/profiles/profile/%s/" % o.username,
}

MARKUP_FILTER_FALLBACK = 'none'
MARKUP_CHOICES = (
    ('restructuredtext', u'reStructuredText'),
    ('textile', u'Textile'),
    ('markdown', u'Markdown'),
    ('creole', u'Creole'),
)
WIKI_MARKUP_CHOICES = MARKUP_CHOICES

AUTH_PROFILE_MODULE = 'profiles.Profile'
#NOTIFICATION_LANGUAGE_MODULE = 'account.Account'

ACCOUNT_OPEN_SIGNUP = True
ACCOUNT_REQUIRED_EMAIL = False
ACCOUNT_EMAIL_VERIFICATION = False

EMAIL_CONFIRMATION_DAYS = 2
#ACCOUNT_ACTIVATION_DAYS = 2
EMAIL_DEBUG = DEBUG
CONTACT_EMAIL = "tintz@tintz.com.br"
SITE_NAME = "Tintz"
LOGIN_URL = "/account/login/"
LOGIN_REDIRECT_URLNAME = "home"

# avatar controls
AVATAR_DEFAULT_URL =  MEDIA_URL + 'images/avatar.png'
AVATAR_GRAVATAR_BACKUP = False

INTERNAL_IPS = (
    '127.0.0.1',
)

ugettext = lambda s: s
LANGUAGES = (
    ('en', u'English'),
)

# URCHIN_ID = "ua-..."

YAHOO_MAPS_API_KEY = "..."

class NullStream(object):
    def write(*args, **kwargs):
        pass
    writeline = write
    writelines = write

RESTRUCTUREDTEXT_FILTER_SETTINGS = {
    'cloak_email_addresses': True,
    'file_insertion_enabled': False,
    'raw_enabled': False,
    'warning_stream': NullStream(),
    'strip_comments': True,
}

# if Django is running behind a proxy, we need to do things like use
# HTTP_X_FORWARDED_FOR instead of REMOTE_ADDR. This setting is used
# to inform apps of this fact
BEHIND_PROXY = False

FORCE_LOWERCASE_TAGS = True

WIKI_REQUIRES_LOGIN = True

#Debug Log
import logging
logging.basicConfig(
    level = logging.DEBUG,
    format = '%(asctime)s %(levelname)s %(message)s',
    filename = '/home/danielfranca/workspace/tintz/log/tintz.log',
    filemode = 'w'
)

# Uncomment this line after signing up for a Yahoo Maps API key at the
# following URL: https://developer.yahoo.com/wsregapp/
# YAHOO_MAPS_API_KEY = ''

# local_settings.py can be used to override environment-specific tintzsettings
# like database and email that differ between development and production.
try:
    from local_settings import *
except ImportError:
    pass


# Haystack
HAYSTACK_SITECONF = 'tintz.search_sites'
HAYSTACK_SEARCH_ENGINE = 'xapian'
HAYSTACK_XAPIAN_PATH = '/home/danielfranca/workspace/tintz/xapian-index'
