#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.template.loader import render_to_string

TEST_RESPONSES = {
    '123-abc-received': render_to_string(template_name='tests/transaction_details.xml', dictionary={'amount': 123, 'status': 'received', 'transaction_id': '123-abc-received'}),
    '123-abc-loss': render_to_string(template_name='tests/transaction_details.xml', dictionary={'amount': 123, 'status': 'loss', 'transaction_id': '123-abc-loss'}),
}
