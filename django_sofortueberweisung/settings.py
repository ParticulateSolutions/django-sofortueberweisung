from django_sofortueberweisung.__init__ import __version__

from django.conf import settings

DJANGO_PAYDIREKT_VERSION = __version__

SOFORT_USER = getattr(settings, 'SOFORT_USER', False)
SOFORT_API_KEY = getattr(settings, 'SOFORT_API_KEY', False)
SOFORT_PROJECT_ID = getattr(settings, 'SOFORT_PROJECT_ID', False)

SOFORT_SUCCESS_REDIRECT = getattr(settings, 'SOFORT_SUCCESS_REDIRECT', True)
SOFORT_SUCCESS_URL = getattr(settings, 'SOFORT_SUCCESS_URL', '/')
SOFORT_ABORT_URL = getattr(settings, 'SOFORT_ABORT_URL', '/')
SOFORT_TIMEOUT_URL = getattr(settings, 'SOFORT_TIMEOUT_URL', '/')
SOFORT_NOTIFICATION_URLS = getattr(settings, 'SOFORT_NOTIFICATION_URLS', [{
    'url': '/sofortueberweisung/notify/',
    'notify_on': 'pending, loss'
}, {
    'url': '/sofortueberweisung/notify/'
}])
SOFORT_NOTIFICATION_EMAILS = getattr(settings, 'SOFORT_NOTIFICATION_EMAILS', [])
SOFORT_CUSTOMER_PROTECTION = getattr(settings, 'SOFORT_CUSTOMER_PROTECTION', False)
SOFORT_LANGUAGE_CODE = getattr(settings, 'SOFORT_LANGUAGE_CODE', None)
SOFORT_TIMEOUT = getattr(settings, 'SOFORT_TIMEOUT', None)
SOFORT_VALID_TRANSACTION_STATUS = getattr(settings, 'SOFORT_VALID_TRANSACTION_STATUS', ['received', 'untraceable', 'pending'])
