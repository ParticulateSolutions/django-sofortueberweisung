import logging
from django.template.loader import render_to_string
from six import python_2_unicode_compatible

from django.db import models
from django.utils.translation import ugettext_lazy as _


@python_2_unicode_compatible
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

    def __str__(self):
        return self.transaction_id

    class Meta:
        verbose_name = _("Sofort transaction")
        verbose_name_plural = _("Sofort transactions")

    def refresh_from_sofort(self, sofort_wrapper):
        xml_data = render_to_string(template_name="django_sofortueberweisung/transaction_update.xml", context={'transactions': [{'id': self.transaction_id}]})
        response = sofort_wrapper.call_api(xml_data=xml_data)
        if not response:
            return False
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
            self.status = transaction_details['status']
            self.status_reason = transaction_details['status_reason']
            self.costs_fees = transaction_details['costs']['fees']
            self.costs_currency_code = transaction_details['costs']['currency_code']
            self.costs_exchange_rate = transaction_details['costs']['exchange_rate']
            self.save()
            return self
        else:
            return False
