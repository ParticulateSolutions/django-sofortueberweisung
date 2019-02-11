# 0.2.0 (2019.02.07)

- Added new model `SofortRefund` to store refund data and base64-encoded PAIN file
- Added new model `SofortError` to store errors on refunds
- Included migration for new models
- new function `create_refund` for `SofortTransaction`
- new function `get_transaction_details` for `SofortTransaction`
- Test cases for succesful and failing refund
- Dropped support for Python 3.2 and 3.3
- Added support for Python 3.6, 3.7 and Django 2.0 and 2.1
