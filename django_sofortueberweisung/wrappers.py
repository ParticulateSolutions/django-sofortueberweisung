import base64
import logging
import os
import sys

import xmltodict
from django.conf import settings
from django.db import IntegrityError
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from django_sofortueberweisung import \
    settings as django_sofortueberweisung_settings
from django_sofortueberweisung.__init__ import __version__
from django_sofortueberweisung.models import SofortTransaction

try:
    # For Python 3.0 and later
    from urllib.error import HTTPError
    from urllib.request import urlopen
    from urllib.request import Request
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import HTTPError, Request, urlopen


class SofortWrapper(object):

    api_url = 'https://api.sofort.com/api/xml'
    interface_version = 'django_sofortueberweisung_v%s' % __version__
    cafile = os.path.join(os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), 'django_sofortueberweisung')), 'cacert.pem')
    auth = None

    def __init__(self, auth=None):
        super(SofortWrapper, self).__init__()
        if getattr(settings, 'SOFORT', False):
            self.auth = auth

    def init(self,
        amount,
        email_customer=None,
        phone_customer=None,
        user_variables=None,
        sender=None,
        reasons=None,
        currency_code='EUR',
        success_url=django_sofortueberweisung_settings.SOFORT_SUCCESS_URL,
        success_link_redirect=django_sofortueberweisung_settings.SOFORT_SUCCESS_REDIRECT,
        abort_url=django_sofortueberweisung_settings.SOFORT_ABORT_URL,
        timeout_url=django_sofortueberweisung_settings.SOFORT_TIMEOUT_URL,
        notification_urls=django_sofortueberweisung_settings.SOFORT_NOTIFICATION_URLS,
        language_code=django_sofortueberweisung_settings.SOFORT_LANGUAGE_CODE):

        if not self.auth:
            return False
        data = {
            'project_id': self.auth['PROJECT_ID'],
            'interface_version': SofortWrapper.interface_version,
            'amount': '%.2f' % amount,
            'currency_code': currency_code,
            'language_code': language_code,
            'email_customer': email_customer,
            'phone_customer': phone_customer,
            'user_variables': user_variables,
            'sender': sender,
            'reasons': reasons,
            'success_url': success_url,
            'success_link_redirect': success_link_redirect,
            'abort_url': abort_url,
            'timeout': django_sofortueberweisung_settings.SOFORT_TIMEOUT,
            'timeout_url': timeout_url,
            'notification_urls': notification_urls,
            'notification_emails': django_sofortueberweisung_settings.SOFORT_NOTIFICATION_EMAILS,
            'customer_protection': django_sofortueberweisung_settings.SOFORT_CUSTOMER_PROTECTION
        }
        xml_data = render_to_string('django_sofortueberweisung/transaction_init.xml', context=data)
        response = self.call_api(xml_data=xml_data)

        if response is False:
            return False
        
        errors = []
        if 'errors' in response:
            for error in response['errors']:
                errors.append(error)

        warnings = []
        new_transaction = {}
        if 'new_transaction' in response:
            new_transaction = response['new_transaction']
            errors = []
            if 'warnings' in new_transaction:
                for warning in new_transaction['warnings']:
                    warnings.append(warning)

        try:
            if errors != {} or warnings != {}:
                logger = logging.getLogger(__name__)
                for error in errors:
                    logger.error("Sofort: ".format(error.get('message', '')))
                for warning in warnings:
                    logger.warning("Sofort: ".format(warning.get('message', '')))
        except:
            pass

        if new_transaction != {}:
            try:
                return SofortTransaction.objects.create(transaction_id=new_transaction['transaction'], payment_url=new_transaction['payment_url'])
            except IntegrityError:
                logger = logging.getLogger(__name__)
                logger.error(_("Sofort: transaction id already in database"))
                return False
        else:
            return False

    def call_api(self, url=None, xml_data=None):
        if not self.auth:
            return False
        if url is None:
            url = SofortWrapper.api_url
        request = Request(url)
        auth_string = base64.b64encode('{0}:{1}'.format(self.auth['USER'], self.auth['API_KEY']).encode('utf-8')).decode('utf-8')
        request.add_header('Authorization', 'Basic {0}'.format(auth_string))
        if xml_data:
            xml_data = xml_data.encode(encoding='utf-8')
            data_len = len(xml_data)
            request.add_header('Content-type', 'application/xml; charset=UTF-8')
            request.add_header('Accept', 'application/xml; charset=UTF-8')
            request.add_header('Content-Length', data_len)
            request.data = xml_data

        try:
            if sys.version_info.major > 2 or (sys.version_info.major == 2 and sys.version_info.major > 7 or (sys.version_info.major == 7 and sys.version_info.major >= 9)):
                response = urlopen(request, cafile=self.cafile)
            else:
                response = urlopen(request)
        except HTTPError as e:
            logger = logging.getLogger(__name__)
            fp = e.fp
            body = fp.read()
            fp.close()
            if hasattr(e, 'code'):
                logger.error("Paydirekt Error {0}({1}): {2}".format(e.code, e.msg, body))
            else:
                logger.error("Paydirekt Error({0}): {1}".format(e.msg, body))
        else:
            if (hasattr(response, 'status') and str(response.status).startswith('2')) or (hasattr(response, 'status_code') and str(response.status_code).startswith('2')) or (hasattr(response, 'code') and str(response.code).startswith('2')):
                response_body = response.read()
                return xmltodict.parse(response_body)
        return False
