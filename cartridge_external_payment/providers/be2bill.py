# -*- coding: utf-8 -*-
from decimal import Decimal

from django_be2bill.sdk import Be2BillForm
from cartridge_external_payment.providers.base import PaymentProvider

class Be2BillProvider(PaymentProvider):
    def get_start_payment_form(self, request, order):
        total = Decimal(order.total * 100).quantize(Decimal('0'))
        fullname = order.billing_detail_first_name + ' ' + \
                    order.billing_detail_last_name
        return Be2BillForm(operation_type="payment",
                           client_ident=request.user.id,
                           description="X",
                           order_id=order.id,
                           amount=total,

                           client_email=order.billing_detail_email,
                           card_full_name=fullname,

                           #Save cart id for notification
                           extra_data=request.cart.id)

    def get_order_id(self, notification_request):
        return notification_request.GET.get('ORDERID', None)

    def get_transaction_id(self, notification_request):
        return notification_request.GET.get('TRANSACTIONID', None)

    def get_cart_id(self, notification_request):
        raise notification_request.GET.get('EXTRADATA', None)
