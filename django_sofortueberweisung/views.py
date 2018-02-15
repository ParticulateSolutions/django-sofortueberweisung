
import xmltodict

from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from django_sofortueberweisung import settings as django_sofortueberweisung_settings
from django_sofortueberweisung.wrappers import SofortWrapper

from .models import SofortTransaction


class NotifySofortView(View):
    sofort_wrapper = SofortWrapper(auth={
        'USER': django_sofortueberweisung_settings.SOFORT_USER,
        'API_KEY': django_sofortueberweisung_settings.SOFORT_API_KEY,
        'PROJECT_ID': django_sofortueberweisung_settings.SOFORT_PROJECT_ID
    })

    def post(self, request, *args, **kwargs):
        request_data = xmltodict.parse(request.body)
        status_notification = {}
        if 'status_notification' in request_data:
            status_notification = request_data['status_notification']

        if 'transaction' in status_notification:
            try:
                sofort_transaction = SofortTransaction.objects.get(transaction_id=status_notification['transaction'])
            except SofortTransaction.DoesNotExist:
                pass
            else:
                return self.handle_updated_transaction(sofort_transaction)
        return HttpResponse(status=400)

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(NotifySofortView, self).dispatch(request, *args, **kwargs)

    def handle_updated_transaction(self, sofort_transaction):
        """
            Override to use the sofort_transaction in the way you want.
        """
        updated_transaction = sofort_transaction.refresh_from_sofort(sofort_wrapper=self.sofort_wrapper)
        if updated_transaction:
            if sofort_transaction.status not in django_sofortueberweisung_settings.SOFORT_VALID_TRANSACTION_STATUS:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(_('Sofort: Status of transaction {} is now {}').format(sofort_transaction.transaction_id, sofort_transaction.status))
            return HttpResponse(status=200)
        return HttpResponse(status=400)
