# -*- coding: utf-8 -*-
from django.core.urlresolvers import get_callable, reverse
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.http import HttpResponse

from mezzanine.conf import settings
from mezzanine.utils.views import set_cookie
from mezzanine.utils.importing import import_dotted_path

from cartridge.shop import checkout
from cartridge.shop.utils import sign
from cartridge.shop.views import billship_handler, order_handler
from cartridge.shop.models import Order, Cart

provider = import_dotted_path(settings.SHOP_PAYMENT_PROVIDER)()

@never_cache
def checkout_steps(request):
    """
    Display the order form and handle processing of each step.
    """
    # Do the authentication check here rather than using standard
    # login_required decorator. This means we can check for a custom
    # LOGIN_URL and fall back to our own login view.
    authenticated = request.user.is_authenticated()
    if settings.SHOP_CHECKOUT_ACCOUNT_REQUIRED and not authenticated:
        url = "%s?next=%s" % (settings.LOGIN_URL, reverse("shop_checkout"))
        return redirect(url)

    # Determine the Form class to use during the checkout process
    form_class = get_callable(settings.SHOP_CHECKOUT_FORM_CLASS)

    step = int(request.POST.get("step", checkout.CHECKOUT_STEP_FIRST))
    initial = checkout.initial_order_data(request)
    form = form_class(request, step, initial=initial)
    data = request.POST
    checkout_errors = []

    if request.POST.get("back") is not None:
        # Back button in the form was pressed - load the order form
        # for the previous step and maintain the field values entered.
        step -= 1
        form = form_class(request, step, initial=initial)
    elif request.method == "POST" and request.cart.has_items():
        form = form_class(request, step, initial=initial, data=data)
        if form.is_valid():
            # Copy the current form fields to the session so that
            # they're maintained if the customer leaves the checkout
            # process, but remove sensitive fields from the session
            # such as the credit card fields so that they're never
            # stored anywhere.
            request.session["order"] = dict(form.cleaned_data)
            sensitive_card_fields = ("card_number", "card_expiry_month",
                                     "card_expiry_year", "card_ccv")
            for field in sensitive_card_fields:
                if field in request.session["order"]:
                    del request.session["order"][field]

            # FIRST CHECKOUT STEP - handle shipping and discount code.
            if step == checkout.CHECKOUT_STEP_FIRST:
                try:
                    billship_handler(request, form)
                except checkout.CheckoutError, e:
                    checkout_errors.append(e)
                form.set_discount()

            # FINAL CHECKOUT STEP has been removed, has payment is now
            # handled by the external provider

            # If any checkout errors, assign them to a new form and
            # re-run is_valid. If valid, then set form to the next step.
            form = form_class(request, step, initial=initial, data=data,
                             errors=checkout_errors)
            if form.is_valid():
                step += 1
                form = form_class(request, step, initial=initial)

    step_vars = checkout.CHECKOUT_STEPS[step - 1]
    template = "shop/%s.html" % step_vars["template"]
    CHECKOUT_STEP_FIRST = step == checkout.CHECKOUT_STEP_FIRST
    context = {"form": form, "CHECKOUT_STEP_FIRST": CHECKOUT_STEP_FIRST,
               "step_title": step_vars["title"], "step_url": step_vars["url"],
               "steps": checkout.CHECKOUT_STEPS, "step": step}

    #===========================================================================
    # External payment management
    #===========================================================================
    context['CHECKOUT_STEP_PAYMENT'] = step == checkout.CHECKOUT_STEP_PAYMENT
    if step == checkout.CHECKOUT_STEP_PAYMENT:
        form = form_class(request, step, initial=initial, data=data)
        order = form.save(commit=False)
        order.setup(request)
        context['start_payment_form'] = provider.get_start_payment_form(request, order)
        print context['start_payment_form'].get_form_target()
    response = render(request, template, context)

    if step == checkout.CHECKOUT_STEP_PAYMENT:
        # Set the cookie for remembering address details
        # if the "remember" checkbox was checked.
        if form.cleaned_data.get("remember") is not None:
            remembered = "%s:%s" % (sign(order.key), order.key)
            set_cookie(response, "remember", remembered,
                       secure=request.is_secure())
        else:
            response.delete_cookie("remember")

    return response

def finalize_order(request):
    '''Helper function that actually complete the order when the
    payment provider tells us so.
    '''
    order_id = provider.get_order_id(request)
    order = Order.objects.get(pk=order_id)
    #Order is already completed
#    if order.payment_done:
#        return


    #Recreate an order form for the order handler
    data = checkout.initial_order_data(request)
    data["step"] = checkout.CHECKOUT_STEP_LAST
    order_form_class = get_callable(settings.SHOP_CHECKOUT_FORM_CLASS)
    form = order_form_class(request, step=checkout.CHECKOUT_STEP_LAST, data=data)
    form.instance = order
    form.full_clean()
    request.session["order"] = dict(form.cleaned_data)

    order.transaction_id = provider.get_transaction_id(request)
    order.payment_done = True
    order.complete(request)

    order_handler(request, form, order)
    checkout.send_order_email(request, order)

def payment_completed(request):
    '''View where the user get redirected after completing a payment
    Finalize the order, and redirect to the confirmation that
    the payment is completed
    '''
    finalize_order(request)
    return redirect("shop_complete")

def payment_notification(request):
    '''View that the external payment provider calls when a payment is succesful.
    Retrieve and the order, then finalize it as in standard cartridge checkout module.
    '''
    #try to simulate the cart for the order_handler that needs it
    try:
        cart_id = provider.get_cart_id(request)
        request.cart = Cart.objects.get(id=cart_id)
    except (NotImplementedError, Cart.DoesNotExist, TypeError):
        pass

    finalize_order(request)
    return HttpResponse()
