from copy import deepcopy

from django.contrib import admin

from cartridge.shop.admin import OrderAdmin
from cartridge.shop.models import  Order

order_fieldsets = deepcopy(admin.site._registry[Order].fieldsets)
order_fieldsets[2][1]["fields"] = list(order_fieldsets[2][1]["fields"])
order_fieldsets[2][1]["fields"].insert(0, 'payment_done')

class ExternalPaymentOrderAdmin(OrderAdmin):
    fieldsets = order_fieldsets
    list_display = ("id", "billing_name", "total", "time", "payment_done",
                    "status", "transaction_id", "invoice")

admin.site.unregister(Order)
admin.site.register(Order, ExternalPaymentOrderAdmin)
