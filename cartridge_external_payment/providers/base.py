# -*- coding: utf-8 -*-

class PaymentProvider(object):
    def get_start_payment_form(self, request, order):
        raise NotImplementedError()
    def get_order_id(self, notification_request):
        raise NotImplementedError()
    def get_transaction_id(self, notification_request):
        raise NotImplementedError()
    def get_cart_id(self, notification_request):
        raise NotImplementedError()
