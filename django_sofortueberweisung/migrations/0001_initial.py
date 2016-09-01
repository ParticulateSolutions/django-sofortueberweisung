# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SofortTransaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('transaction_id', models.CharField(unique=True, max_length=255, verbose_name='transaction id')),
                ('status', models.CharField(max_length=255, verbose_name='status', blank=True)),
                ('status_reason', models.CharField(max_length=255, verbose_name='status reason', blank=True)),
                ('payment_url', models.URLField(verbose_name='payment url')),
                ('costs_fees', models.CharField(max_length=255, verbose_name='status reason', blank=True)),
                ('costs_currency_code', models.CharField(max_length=255, verbose_name='status reason', blank=True)),
                ('costs_exchange_rate', models.CharField(max_length=255, verbose_name='status reason', blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('last_modified', models.DateTimeField(auto_now=True, verbose_name='last modified')),
            ],
            options={
                'ordering': ['-created_at'],
                'verbose_name': 'Sofort transaction',
                'verbose_name_plural': 'Sofort transactions',
            },
        ),
    ]
