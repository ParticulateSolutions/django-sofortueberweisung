import logging
import urllib2

from django.conf import settings
from django.db import models, IntegrityError
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

import xmltodict


class SofortTransaction(models.Model):
    transaction_id = models.CharField(_("transaction id"), max_length=255, unique=True)
    status = models.CharField(_("status"), max_length=255, blank=True)
    status_reason = models.CharField(_("status reason"), max_length=255, blank=True)
    payment_url = models.URLField(_("payment url"))

    costs_fees = models.CharField(_("status reason"), max_length=255, blank=True)
    costs_currency_code = models.CharField(_("status reason"), max_length=255, blank=True)
    costs_exchange_rate = models.CharField(_("status reason"), max_length=255, blank=True)

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    last_modified = models.DateTimeField(_("last modified"), auto_now=True)

    objects = models.Manager()

    def __unicode__(self):
        return _("Sofort transaction: {}".format(self.transaction_id))

    def __str__(self):
        return _("Sofort transaction: {}".format(self.transaction_id))

    class Meta:
        verbose_name = _("Sofort transaction")
        verbose_name_plural = _("Sofort transactions")
        ordering = ["-created_at"]


class SofortWrapper(object):

    api_url = 'https://api.sofort.com/api/xml'
    interface_version = 'django_sofortueberweisung_v1.0.0'
    auth = None

    def __init__(self, auth=None):
        super(SofortWrapper, self).__init__()
        self.auth = auth

    def init(self, amount, email_customer=None, phone_customer=None, user_variables=None, sender=None, reasons=None, currency_code='EUR',
             success_url=settings.SOFORT_SUCCESS_URL, success_link_redirect=settings.SOFORT_SUCCESS_REDIRECT, abort_url=settings.SOFORT_ABORT_URL,
             timeout_url=settings.SOFORT_TIMEOUT_URL, notification_urls=settings.SOFORT_NOTIFICATION_URLS):
        data = {
            'project_id': self.auth['PROJECT_ID'],
            'interface_version': SofortWrapper.interface_version,
            'amount': '%.2f' % amount,
            'currency_code': currency_code,
            'language_code': settings.SOFORT_LANGUAGE_CODE,
            'timeout': settings.SOFORT_TIMEOUT,
            'email_customer': email_customer,
            'phone_customer': phone_customer,
            'user_variables': user_variables,
            'sender': sender,
            'reasons': reasons,
            'success_url': success_url,
            'success_link_redirect': success_link_redirect,
            'abort_url': abort_url,
            'timeout_url': timeout_url,
            'notification_urls': notification_urls,
            'notification_emails': settings.SOFORT_NOTIFICATION_EMAILS,
            'customer_protection': settings.SOFORT_CUSTOMER_PROTECTION
        }
        xml_data = render_to_string('django_sofortueberweisung/transaction_init.xml', context=data)
        response = self._call_api(xml_data=xml_data)

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
                for warning in response['warnings']:
                    warnings.append(warning)

        if errors != {} or warnings != {}:
            logger = logging.getLogger(__name__)
            for error in errors:
                logger.error("Sofort: ".format(error))
            for warning in warnings:
                logger.warning("Sofort: ".format(warning))
        if new_transaction != {}:
            try:
                return SofortTransaction.objects.create(transaction_id=new_transaction['transaction'], payment_url=new_transaction['payment_url'])
            except IntegrityError:
                logger = logging.getLogger(__name__)
                logger.error(_("Sofort: transaction id already in database"))
                return False
        else:
            return False

    def update_transaction(self, sofort_transaction):
        xml_data = render_to_string(template_name="django_sofortueberweisung/transaction_update.xml", context={'transactions': [{'id': sofort_transaction.transaction_id}]})
        response = self._call_api(xml_data=xml_data)
        errors = []
        if 'errors' in response:
            for error in response['errors']:
                errors.append(error)

        transaction_details = {}
        if 'transactions' in response and response['transactions'] is not None and 'transaction_details' in response['transactions']:
            transaction_details = response['transactions']['transaction_details']

        if errors != {}:
            logger = logging.getLogger(__name__)
            for error in errors:
                logger.error("Sofort: ".format(error))

        if 'status' in transaction_details and transaction_details['status'] is not None:
            sofort_transaction.status = transaction_details['status']
            sofort_transaction.status_reason = transaction_details['status_reason']
            sofort_transaction.costs_fees = transaction_details['costs']['fees']
            sofort_transaction.costs_currency_code = transaction_details['costs']['currency_code']
            sofort_transaction.costs_exchange_rate = transaction_details['costs']['exchange_rate']
            sofort_transaction.save()
            return sofort_transaction
        else:
            return False

    def _call_api(self, url=None, xml_data=None):
        if url is None:
            url = SofortWrapper.api_url
        request = urllib2.Request(url)
        if self.auth:
            auth_string = '{0}:{1}'.format(self.auth['USER'], self.auth['API_KEY']).encode('base64').replace('\n', '')
            request.add_header('Authorization', 'Basic {0}'.format(auth_string))
        if xml_data:
            data_len = len(xml_data)
            request.add_header('Content-type', 'application/xml; charset=UTF-8')
            request.add_header('Accept', 'application/xml; charset=UTF-8')
            request.add_header('Content-Length', data_len)
            request.add_data(xml_data)

        response = urllib2.urlopen(request)
        response_body = response.read()
        return xmltodict.parse(response_body)
