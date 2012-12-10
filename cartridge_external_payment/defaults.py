from django.utils.translation import ugettext_lazy as _

from mezzanine.conf import register_setting

register_setting(
        name="SHOP_PAYMENT_PROVIDER",
        label=_("External payment provider"),
        description=_("Connector class to the payment provider"),
        editable=False,
        default='cartridge_external_payment.providers.base.PaymentProvider',
)
