#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os, sys
import re
import xmltodict
from requests import Response
from testfixtures import replace

from django.conf.urls import include, url
from django.test import Client, TestCase

from django_sofortueberweisung import settings as django_sofortueberweisung_settings
from django_sofortueberweisung.models import SofortTransaction
from django_sofortueberweisung.wrappers import SofortWrapper, DjangoSofortError

from .test_response_mockups import TEST_RESPONSES

try:
    # For Python 3.0 and later
    from urllib.error import HTTPError
    from urllib.request import urlopen
    from urllib.request import Request
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import HTTPError, Request, urlopen

app_name='sofort'
urlpatterns = [
    url(r'^sofort/$', include('django_sofortueberweisung.urls')),
]


def mock_generate_uuid(length=12):
    return '12345678901234567890'


def mock_urlopen(request, cafile=None):
    response = {}
    url = request.get_full_url()
    try:
        data = xmltodict.parse(request.data)
    except:
        data = {}
    try:
        if url == 'https://api.sofort.com/api/xml':
            if 'transaction_request' in data:
                if 'transaction' in data['transaction_request']:
                    if data['transaction_request']['transaction'] == '123-abc-received':
                        response = TEST_RESPONSES['123-abc-received']
                    elif data['transaction_request']['transaction'] == '123-abc-loss':
                        response = TEST_RESPONSES['123-abc-loss']
            elif 'refunds' in data:
                transaction = data['refunds']['refund']['transaction']
                if transaction == '123-refund-error':
                    response = TEST_RESPONSES['refund-transaction-invalid'](transaction)
                else:
                    response = TEST_RESPONSES['refund-transaction-valid'](transaction)
    except KeyError:
        response = False
        result = MockResponse(response)
    else:
        result = MockResponse(response)
        result.headers.update({'Content-type': 'application/xml; charset=UTF-8'})
        result.headers.update({'Accept': 'application/xml; charset=UTF-8'})
    return result


class MockResponse(Response):
    response = ''

    def __init__(self, response):
        super(MockResponse, self).__init__()
        if not response:
            self.status = 404
        else:
            self.status = 200
        self.response = response

    def read(self):
        return self.response


class TestSofortNotifications(TestCase):
    sofort_wrapper = None

    def setUp(self):
        self.sofort_wrapper = SofortWrapper(auth={
            'USER': django_sofortueberweisung_settings.SOFORT_USER,
            'API_KEY': django_sofortueberweisung_settings.SOFORT_API_KEY,
            'PROJECT_ID': django_sofortueberweisung_settings.SOFORT_PROJECT_ID
        })

    # testing valid transaction
    @replace('django_sofortueberweisung.wrappers.urlopen', mock_urlopen)
    def test_get_notify(self):
        client = Client()
        response = client.get('/sofort/notify/')
        self.assertEqual(response.status_code, 405)

    @replace('django_sofortueberweisung.wrappers.urlopen', mock_urlopen)
    def test_known_transaction_known_at_sofort_received(self):
        client = Client()
        self._create_test_transaction(transaction_id='123-abc-received')
        post_data = {'status_notification': {'transaction': '123-abc-received'}}
        xml_data = xmltodict.unparse(post_data)
        response = client.post('/sofort/notify/', data=xml_data, content_type='application/hal+json')
        self.assertEqual(response.status_code, 200)

    @replace('django_sofortueberweisung.wrappers.urlopen', mock_urlopen)
    def test_known_transaction_known_at_sofort_loss(self):
        client = Client()
        self._create_test_transaction(transaction_id='123-abc-loss')
        post_data = {'status_notification': {'transaction': '123-abc-loss'}}
        xml_data = xmltodict.unparse(post_data)
        response = client.post('/sofort/notify/', data=xml_data, content_type='application/hal+json')
        self.assertEqual(response.status_code, 200)

    @replace('django_sofortueberweisung.wrappers.urlopen', mock_urlopen)
    def test_known_transaction_unknown_at_sofort(self):
        client = Client()
        self._create_test_transaction(transaction_id='123-abc-unknown')
        post_data = {'status_notification': {'transaction': '123-abc-unknown'}}
        xml_data = xmltodict.unparse(post_data)
        self.assertRaises(Exception, client.post, '/sofort/notify/', data=xml_data, content_type='application/hal+json')

    # TODO: Test XML response
    @replace('django_sofortueberweisung.wrappers.urlopen', mock_urlopen)
    def test_known_transaction_refund(self):
        self._create_test_transaction(transaction_id='123-abc-received')
        transaction = SofortTransaction.objects.get(transaction_id='123-abc-received')
        refund = transaction.create_refund(self.sofort_wrapper, sender_data={'owner': 'Test Person', 'iban': 'DE11888888889999999999',
                                                                        'bic': 'SFRTDE20XXX'}, amount=2.40)
        self.assertEqual(transaction.transaction_id, refund.transaction.transaction_id)
        self.assertEqual(transaction, refund.transaction)
        self.assertEqual(refund.status, 'accepted')
        if sys.version_info[0] < 3:
            self.assertRegexpMatches(refund.pain, re.compile('^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$'))
        else:
            self.assertRegex(refund.pain, re.compile('^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$'))

    @replace('django_sofortueberweisung.wrappers.urlopen', mock_urlopen)
    def test_known_transaction_refund_error(self):
        self._create_test_transaction(transaction_id='123-refund-error')
        transaction = SofortTransaction.objects.get(transaction_id='123-refund-error')
        refund = transaction.create_refund(self.sofort_wrapper, sender_data={'owner': 'Test Person', 'iban': 'DE11888888889999999999',
                                                                        'bic': 'SFRTDE20XXX'}, amount=2.40)
        self.assertEqual(transaction.transaction_id, refund.transaction.transaction_id)
        self.assertEqual(transaction, refund.transaction)
        self.assertEqual(refund.status, 'error')
        self.assertGreaterEqual(refund.errors.count(), 1)
        self.assertTrue(refund.errors.filter(error_code='5003'))


    def _create_test_transaction(self, transaction_id):
        return SofortTransaction.objects.create(
            transaction_id=transaction_id,
            payment_url='https://www.sofort.com/payment/go/'+transaction_id
        )


class TestSofortTransactions(TestCase):
    auth = {
        'PROJECT_ID': '299010',
        'USER': '135335',
        'API_KEY': 'aeb2075b1455a8ce874749e973e61cca',
    }
    cafile = os.path.join(os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), 'django_sofortueberweisung')), 'cacert.pem')

    def test_valid_transaction(self):
        sofort_wrapper = SofortWrapper(auth=self.auth)
        sofort_transaction = sofort_wrapper.init(
            amount=1.0,
            email_customer='tech@particulate.me',
            phone_customer=None,
            user_variables=None,
            sender='Test',
            reasons=['Just a test.'],
            currency_code='EUR'
        )
        self.assertEqual(sofort_transaction.status, '')
        # TODO: let the transaction be accepted by sofort.com
        # TODO: let the transaction be refunded by sofort.com
        self.assertFalse(sofort_transaction.refresh_from_sofort(sofort_wrapper=sofort_wrapper))
