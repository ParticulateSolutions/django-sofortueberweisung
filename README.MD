# django-sofortueberweisung [![Build Status](https://travis-ci.org/ParticulateSolutions/django-sofortueberweisung.svg?branch=master)](https://travis-ci.org/ParticulateSolutions/django-sofortueberweisung)


## What do you need for django-sofortueberweisung?

1. An account on sofort.com
2. Django >= 1.8
3. xmltodict >= 0.9.2

## How to install django-sofortueberweisung?

There are just two steps needed to install django-sofortueberweisung:

1. Install django-sofortueberweisung to your virtual env:

	```bash
	pip install django-sofortueberweisung
	```

2. Configure your django installation with the following lines:

	```python
    # django-sofortueberweisung
    INSTALLED_APPS += ('django_sofortueberweisung', )

    SOFORT = True
    SOFORT_USER = '99999'
    SOFORT_API_KEY = 'a12b34cd567890123e456f7890123456'
    SOFORT_PROJECT_ID = '999999'
    SOFORT_SUCCESS_URL = 'https://www.example.com/'
    SOFORT_SUCCESS_REDIRECT = True
    SOFORT_ABORT_URL = 'https://www.example.com/abort/'
    SOFORT_TIMEOUT_URL = 'https://www.example.com/timeout/'
    SOFORT_NOTIFICATION_URLS = [{
        'url': 'https://www.example.com/sofortueberweisung/notify/',
        'notify_on': 'pending, loss'
    }, {
        'url': 'https://www.example.com/sofortueberweisung/notify/'
    }]
    SOFORT_NOTIFICATION_EMAILS = [{
        'email': 'someone@example.com',
        'notify_on': 'pending, loss'
    }, {
        'email': 'sometwo@example.com'
    }]
    SOFORT_CUSTOMER_PROTECTION = False
    SOFORT_LANGUAGE_CODE = None
    SOFORT_TIMEOUT = None
    SOFORT_VALID_TRANSACTION_STATUS = ['received', 'untraceable', 'pending']
	```

3. Use methods for initialization and updating transaction where you need it:

    Initialization:

	```python
	sofort_payment = SofortWrapper(auth={
                        'USER': settings.SOFORT_USER,
                        'API_KEY': settings.SOFORT_API_KEY,
                        'PROJECT_ID': settings.SOFORT_PROJECT_ID
                    })
    sofort_payment.init(amount=10.0)
	```

    Include the notification View in your URLs:

	```python
    # urls.py
    from django.conf.urls import include, url

    urlpatterns = [
        url('^sofortueberweisung/', include('django_sofortueberweisung.urls')),
    ]
	```
	
## refunds

To initiate a refund, you need to pass an `instance` of `SofortWrapper` as first parameter, and `sender_data` as second.
`sender_data` should be a `dict` containing keys for `holder`, `iban` and `bic`. Those are your own bank details, not the receiver's.
 
 Refunds are sent with test data by default. To use the values passed for `sender_data` change `SOFORT_REFUNDS_TEST` 
 inside your settings to `False`.
 
```python
sofort_transaction = SofortTransaction.objects.get(transaction_id=<transaction_id>)
sofort_transaction.create_refund(sofort_wrapper, sender_data, <optional params>)
```
This will create and return an instance of `SofortRefund` if request has been successful. If errors have occurred, 
relations to `SofortError` are being created.

For more options, read the code and Sofort API documentation