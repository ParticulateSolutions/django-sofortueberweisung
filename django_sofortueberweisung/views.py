from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

import xmltodict

from .models import SofortTransaction, SofortWrapper


class NotifySofortView(View):
    sofort_wrapper = SofortWrapper(auth={
                        'USER': settings.SOFORT_USER,
                        'API_KEY': settings.SOFORT_API_KEY,
                        'PROJECT_ID': settings.SOFORT_PROJECT_ID
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
        updated_transaction = self.sofort_wrapper.update_transaction(sofort_transaction)
        if updated_transaction:
            if updated_transaction.status not in settings.SOFORT_VALID_TRANSACTION_STATUS:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(_('Sofort: Status of transaction {} is now {}').format(updated_transaction.transaction_id, updated_transaction.status))
            return HttpResponse(status=202)
        return HttpResponse(status=400)
