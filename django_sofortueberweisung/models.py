import logging
from django.template.loader import render_to_string
from six import python_2_unicode_compatible

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from django_sofortueberweisung import settings as django_sofortueberweisung_settings


@python_2_unicode_compatible
class SofortError(models.Model):
    error_code = models.CharField(_('error code'), max_length=30)
    error_message = models.CharField(_('error code'), max_length=255)
    objects = models.Manager()

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    last_modified = models.DateTimeField(_("last modified"), auto_now=True)

    def __str__(self):
        return "{0} - {1}".format(self.error_code, self.error_message)


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

    def log_errors(self, response):
        errors = []
        if "errors" in response:
            for error in response["errors"]:
                errors.append(error)
        if errors != {}:
            logger = logging.getLogger(__name__)
            for error in errors:
                logger.error("Sofort [Refund]: ".format(error))

    def refresh_from_sofort(self, sofort_wrapper):
        xml_data = render_to_string(template_name="django_sofortueberweisung/transaction_update.xml", context={'transactions': [{'id': self.transaction_id}]})
        response = sofort_wrapper.call_api(xml_data=xml_data)
        if not response:
            return False

        self.log_errors(response)

        transaction_details = {}
        if 'transactions' in response and response['transactions'] is not None and 'transaction_details' in response['transactions']:
            transaction_details = response['transactions']['transaction_details']

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

    def get_transaction_details(self, sofort_wrapper):
        xml_data = render_to_string(template_name="django_sofortueberweisung/transaction_update.xml",
                                    context={"transactions": [{"id": self.transaction_id}]})
        response = sofort_wrapper.call_api(xml_data=xml_data)
        return response["transactions"].get("transaction_details") or {} if response and response.get(
            "transactions") else {}

    def create_refund(self, sofort_wrapper, sender_data, amount=None, reasons=None, partial_refund_id=None,
                      refund_title=None, get_data_from_api=False):
        if get_data_from_api:
            refund_data = self.get_transaction_details(sofort_wrapper)
            amount = refund_data.get("amount")
            reasons = refund_data["reasons"]
        if not amount:
            raise ValueError("No amount for refund given/received from Sofort API")
        if not refund_title:
            refund_title = "Refund [{0}] - {1}".format(self.transaction_id, timezone.now().isoformat())
        xml_data = render_to_string(template_name="django_sofortueberweisung/transaction_refund.xml",
                                    context={"transaction_id": self.transaction_id, "sender": sender_data,
                                             "amount": amount, "reasons": reasons, "title": refund_title,
                                             "partial_refund_id": partial_refund_id,
                                             "test": django_sofortueberweisung_settings.SOFORT_REFUNDS_TEST})
        response = sofort_wrapper.call_api(xml_data=xml_data)
        if not response:
            return False

        self.log_errors(response)

        if "refunds" in response and "refund" in response["refunds"] and response["refunds"]["refund"].get("status"):
            errors = []
            if response["refunds"]["refund"].get("errors"):
                error = response["refunds"]["refund"]["errors"].get('error')
                errors.append(SofortError.objects
                              .get_or_create(error_code=str(error.get('code')) if error.get('code') else None,
                                             error_message=error.get('message')))
            sofort_refund = SofortRefund.objects.create(transaction=self, status=response["refunds"]["refund"]["status"],
                                               pain=response["refunds"].get("pain"),
                                               amount=response["refunds"]["refund"]["amount"],
                                               title=response["refunds"].get("title"))
            for error in errors:
                sofort_refund.errors.add(error[0])
            return sofort_refund


@python_2_unicode_compatible
class SofortRefund(models.Model):
    transaction = models.ForeignKey(SofortTransaction, verbose_name=_("Transaction"), related_name="refunds",
                                    on_delete=models.SET_NULL, null=True)
    status = models.CharField(_("status"), max_length=255, blank=True)
    title = models.CharField(_("Title"), max_length=255, blank=True, null=True)
    amount = models.DecimalField(_('Amount'), max_digits=8, decimal_places=2)
    pain = models.TextField(_("PAIN base64"), null=True)
    errors = models.ManyToManyField('SofortError', verbose_name=_('errors'), related_name='refunds')

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    last_modified = models.DateTimeField(_("last modified"), auto_now=True)

    objects = models.Manager()

    def __str__(self):
        return "Refund [{0}] - {1}".format(self.transaction.transaction_id, self.status)
