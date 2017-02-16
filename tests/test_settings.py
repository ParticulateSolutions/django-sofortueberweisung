# Django settings for testproject project.
from django.conf import settings

settings.configure(
    ALLOWED_HOSTS=['*'],
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:'
        }
    },
    ROOT_URLCONF='tests.test_urls',
    INSTALLED_APPS=(
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.staticfiles',
        'django_sofortueberweisung',
        'tests',
    ),

    SOFORT=True,
    SOFORT_USER='135335',
    SOFORT_API_KEY='aeb2075b1455a8ce874749e973e61cca',
    SOFORT_PROJECT_ID='299010',
    SOFORT_SUCCESS_URL='https://www.example.com/',
    SOFORT_SUCCESS_REDIRECT=True,
    SOFORT_ABORT_URL='https://www.example.com/abort/',
    SOFORT_TIMEOUT_URL='https://www.example.com/timeout/',
    SOFORT_NOTIFICATION_URLS=[{
        'url': 'https://www.example.com/sofortueberweisung/notify/',
        'notify_on': 'pending, loss'
    }, {
        'url': 'https://www.example.com/sofortueberweisung/notify/'
    }],
    SOFORT_NOTIFICATION_EMAILS=[{
        'email': 'someone@example.com',
        'notify_on': 'pending, loss'
    }, {
        'email': 'sometwo@example.com'
    }],
    SOFORT_CUSTOMER_PROTECTION=False,
    SOFORT_LANGUAGE_CODE=None,
    SOFORT_TIMEOUT=None,
    SOFORT_VALID_TRANSACTION_STATUS=['received', 'loss', 'refunded',  'untraceable', 'pending']
)
