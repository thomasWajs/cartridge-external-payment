# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns("cartridge_external_payment.views",
    url("^checkout/$", "checkout_steps", name="shop_checkout"),

    url("^payment-completed/$", "payment_completed", name="payment_completed"),
    url("^payment-notification/$", "payment_notification", name="payment_notification"),
)


