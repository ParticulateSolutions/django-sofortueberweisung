# 0.2.1 (2019.05.10)

### Breaking Changes

- `init` doesn't return `False` anymore if API set up/request has failed. Instead it now returns an Exception elaborating on what has happened.
- Several `loggers` replaced by Exceptions. If you rely on logging you can still catch those exceptions and gain more control over your logging.


# 0.2.0 (2019.02.07)

- Added new model `SofortRefund` to store refund data and base64-encoded PAIN file
- Added new model `SofortError` to store errors on refunds
- Included migration for new models
- new function `create_refund` for `SofortTransaction`
- new function `get_transaction_details` for `SofortTransaction`
- Test cases for succesful and failing refund
- Dropped support for Python 3.2 and 3.3
- Added support for Python 3.6, 3.7 and Django 2.0 and 2.1
