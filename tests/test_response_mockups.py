#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.template.loader import render_to_string
from django.utils import timezone


def get_refund_transaction_valid(transaction_id):
    return render_to_string(template_name='tests/transaction_refund.xml',
                            context={'transaction': transaction_id, 'amount': 1.00, 'time': timezone.now(),
                                     'status': 'accepted'})


def get_refund_transaction_invalid(transaction_id):
    return render_to_string(template_name='tests/transaction_refund_error.xml',
                            context={'transaction': transaction_id, 'amount': 1.00, 'time': timezone.now(),
                                     'errors': [{'code': 5003, 'message': 'Amount must not exceed transaction amount.'}]})


TEST_RESPONSES = {
    '123-abc-received': render_to_string(template_name='tests/transaction_details.xml', context={'amount': 123, 'status': 'received', 'transaction_id': '123-abc-received'}),
    '123-abc-loss': render_to_string(template_name='tests/transaction_details.xml', context={'amount': 123, 'status': 'loss', 'transaction_id': '123-abc-loss'}),
    'refund-transaction-valid': get_refund_transaction_valid,
    'refund-transaction-invalid': get_refund_transaction_invalid,
}
