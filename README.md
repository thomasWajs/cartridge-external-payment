cartridge-external-payment
=============

Integration of Cartridge/Mezzanine with payment providers that requires to redirect the
buyer on a form on their platform.

## Installation

Working in your project's [virtualenv](http://www.virtualenv.org/en/latest/index.html):
```
git clone https://github.com/thomasWajs/cartridge-external-payment.git
cd cartridge-external-payment
python setup.py install
```


### Application

Add `'cartridge_external_payment'` to your settings.INSTALLED_APPS, before `'cartridge.shop'`

### Order Form

Set the alternative OrderForm class for the checkout process (see cartridge documentation):

```
SHOP_CHECKOUT_FORM_CLASS = 'cartridge_external_payment.forms.ExternalPaymentOrderForm'
```

This allow to hide payment fields during the payment step at checkout.

### Urls

You must includes the cartridge_external_payment urls in your urls configuration file,
before the cartridge inclusion :

```
urlpatterns = patterns("",
	("^shop/", include("cartridge_external_payment.urls")),
	("^shop/", include("cartridge.shop.urls")),
	[...]
)
```

### Payment provider connector

You must define the connector that will allows to start the payment process
and retrieve order datas when the buyer comes back.
The connector should implements the providers.base.PaymentProvider interface.

```
SHOP_PAYMENT_PROVIDER = 'cartridge_external_payments.providers.be2bill.Be2BillProvider'
```

You can find an exemple implementation by looking at the providers directory.