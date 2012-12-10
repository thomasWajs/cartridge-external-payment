# -*- coding: utf-8 -*-
from cartridge.shop.forms import OrderForm

class ExternalPaymentOrderForm(OrderForm):
    """
    Main Form for the checkout process - ModelForm for the Order Model
    with extra fields for credit card. Used across each step of the
    checkout process with fields being hidden where applicable.
    """
    def __init__(self, *args, **kwargs):
        super(ExternalPaymentOrderForm, self).__init__(*args, **kwargs)
        del self.fields['card_expiry_year']

for field in ('card_name', 'card_type', 'card_number', 'card_expiry_month', 'card_ccv'):
    del ExternalPaymentOrderForm.base_fields[field]
