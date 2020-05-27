import random
from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth import views as django_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse, reverse_lazy
from django.utils.translation import pgettext, ugettext_lazy as _
from django.views.decorators.http import require_POST, require_http_methods
from django.core.mail import send_mail
import random

from ..account import events as account_events
from ..checkout.utils import find_and_assign_anonymous_checkout
from ..core.utils import get_paginator_items
from ..partner.utils import update_partner
from .emails import send_account_delete_confirmation_email
from .forms import (
    ChangePasswordForm,
    LoginForm,
    NameForm,
    PasswordResetForm,
    SignupForm,
    get_address_form,
    logout_on_password_change
)
from .models import User
import nexmo


@find_and_assign_anonymous_checkout()
def login(request):
    kwargs = {"template_name": "account/login.html", "authentication_form": LoginForm}
    return django_views.LoginView.as_view(**kwargs)(request, **kwargs)


@login_required
def logout(request):
    auth.logout(request)
    messages.success(request, _("You have been successfully logged out."))
    return redirect(settings.LOGIN_REDIRECT_URL)


def signup(request):
    form = SignupForm(request.POST or None)
    if form.is_valid():
        form.save()
        password = form.cleaned_data.get("password")
        email = form.cleaned_data.get("email")
        user = auth.authenticate(request=request, email=email, password=password)
        if user:
            auth.login(request, user)
        messages.success(request, _("User has been created"))
        redirect_url = request.POST.get("next", settings.LOGIN_REDIRECT_URL)
        return redirect(redirect_url)
    ctx = {"form": form}
    return TemplateResponse(request, "account/signup.html", ctx)


def password_reset(request):
    kwargs = {
        "template_name": "account/password_reset.html",
        "success_url": reverse_lazy("account:reset-password-done"),
        "form_class": PasswordResetForm,
    }
    return django_views.PasswordResetView.as_view(**kwargs)(request, **kwargs)


class PasswordResetConfirm(django_views.PasswordResetConfirmView):
    template_name = "account/password_reset_from_key.html"
    success_url = reverse_lazy("account:reset-password-complete")
    token = None
    uidb64 = None

    def form_valid(self, form):
        response = super(PasswordResetConfirm, self).form_valid(form)
        account_events.customer_password_reset_event(user=self.user)
        return response


def password_reset_confirm(request, uidb64=None, token=None):
    kwargs = {
        "template_name": "account/password_reset_from_key.html",
        "success_url": reverse_lazy("account:reset-password-complete"),
        "token": token,
        "uidb64": uidb64,
    }
    return PasswordResetConfirm.as_view(**kwargs)(request, **kwargs)


@login_required
def details(request):
    password_form = get_or_process_password_form(request)
    name_form = get_or_process_name_form(request)
    orders = request.user.orders.confirmed().prefetch_related("lines")
    orders_paginated = get_paginator_items(
        orders, settings.PAGINATE_BY, request.GET.get("page")
    )
    ctx = {
        "addresses": request.user.addresses.all(),
        "orders": orders_paginated,
        "change_password_form": password_form,
        "user_name_form": name_form,
    }

    return TemplateResponse(request, "account/details.html", ctx)


def get_or_process_password_form(request):
    form = ChangePasswordForm(data=request.POST or None, user=request.user)
    if form.is_valid():
        form.save()
        logout_on_password_change(request, form.user)
        messages.success(
            request, pgettext("Storefront message", "Password successfully changed.")
        )
    return form


def get_or_process_name_form(request):
    form = NameForm(data=request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
        messages.success(
            request, pgettext("Storefront message", "Account successfully updated.")
        )
    return form


@login_required
def address_edit(request, pk):
    address = get_object_or_404(request.user.addresses, pk=pk)
    address_form, preview = get_address_form(
        request.POST or None, instance=address, country_code=address.country.code
    )
    if address_form.is_valid() and not preview:
        address = address_form.save()
        request.extensions.change_user_address(
            address, address_type=None, user=request.user
        )
        message = pgettext("Storefront message", "Address successfully updated.")
        messages.success(request, message)
        return HttpResponseRedirect(reverse("account:details") + "#addresses")
    return TemplateResponse(
        request, "account/address_edit.html", {"address_form": address_form}
    )


@login_required
def address_delete(request, pk):
    address = get_object_or_404(request.user.addresses, pk=pk)
    if request.method == "POST":
        address.delete()
        messages.success(
            request, pgettext("Storefront message", "Address successfully removed")
        )
        return HttpResponseRedirect(reverse("account:details") + "#addresses")
    return TemplateResponse(
        request, "account/address_delete.html", {"address": address}
    )


@login_required
@require_POST
def account_delete(request):
    user = User.objects.get(pk=request.user.pk)
    send_account_delete_confirmation_email(user)
    messages.success(
        request,
        pgettext(
            "Storefront message, when user requested his account removed",
            "Please check your inbox for a confirmation e-mail.",
        ),
    )
    return HttpResponseRedirect(reverse("account:details") + "#settings")


@login_required
def account_delete_confirm(request, token):
    user = User.objects.get(pk=request.user.pk)

    if not default_token_generator.check_token(user, token):
        raise Http404("No such page!")

    if request.method == "POST":
        user.delete()
        msg = pgettext(
            "Account deleted",
            "Your account was deleted successfully. "
            "In case of any trouble or questions feel free to contact us.",
        )
        messages.success(request, msg)
        return redirect("home")

    return TemplateResponse(request, "account/account_delete_prompt.html")

@login_required
@require_http_methods(["GET", "POST"])
def newPartner(request):
    user = User.objects.get(pk=request.user.pk)

    if request.method == 'POST':
        data_dict = request.POST.dict()

        # Step 1 request
        if 'step_1_req' in data_dict.keys():
            handler = False
            try:
                address_form, preview = get_address_form(
                    request.POST or None, country_code=None
                )
            except:
                address_form, preview = get_address_form(
                    None, 'US'
                )
                handler = True
            if not address_form.is_valid() or handler:
                ctx = {'form': address_form}
                return TemplateResponse(request, 'account/partner/step_1.html', ctx)
              
            newPartner.address = address_form.save()

            if request.session['email_send'] == 'no':
                send_mail(
                    'Partner verification code',
                    'Partner verification code: ' + str(request.session['email_code']),
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                request.session['email_send'] = 'yes'
            return TemplateResponse(request, 'account/partner/step_2.html')

        # Step 2 requests
        elif 'resend_email' in data_dict.keys():
            request.session['email_code'] = random.randint(100000, 999999)
            send_mail(
                'Partner verification code',
                'Partner verification code: ' + str(request.session['email_code']),
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            return TemplateResponse(request, 'account/partner/step_2.html')

        elif 'email_code' in data_dict.keys():
            if int(data_dict['email_code']) == request.session['email_code']:
                if request.session['sms_send'] == 'no':
                    client = nexmo.Client(key = settings.NEXMO_API_KEY,
                                            secret = settings.NEXMO_SECRET)
                    client.send_message({

                        'from': 'saleor',
                        'to': str(newPartner.address.phone),
                        'text': 'Partner verification code: ' + str(request.session['sms_code'])})

                    request.session['sms_send'] = 'yes'

                    print(str(newPartner.address.phone))
                    print(str(request.session['sms_code']))
                return TemplateResponse(request, 'account/partner/step_3.html')
            else:
                return TemplateResponse(request, 'account/partner/step_2.html')

        # Step 3 requests
        elif 'resend_sms' in data_dict.keys():
            request.session['sms_code'] = random.randint(1000, 9999)
            client = nexmo.Client(key = settings.NEXMO_API_KEY,
                                    secret = settings.NEXMO_SECRET)
            client.send_message({

                'from': 'saleor',
                'to': str(newPartner.address.phone),
                'text': 'Partner verification code: ' + str(request.session['sms_code'])}
            )
            print(str(newPartner.address.phone))
            print(str(request.session['sms_code']))

            return TemplateResponse(request, 'account/partner/step_3.html')

        elif 'sms_code' in data_dict.keys():
            if int(data_dict['sms_code']) == request.session['sms_code']:

                user.default_billing_address = newPartner.address
                user.default_billing_address.save()
                user.is_partner = True
                user.first_name = newPartner.address.first_name
                user.last_name= newPartner.address.last_name
                user.phone = newPartner.address.phone
                user.save()

                update_partner(user)

                error=False

                try:
                    del request.session['email_code']
                except:
                    pass
                try:
                    del request.session['email_send']
                except:
                    pass
                try:
                    del request.session['sms_code']
                except:
                    pass
                try:
                    del request.session['sms_send']
                except:
                    pass

                ctx = {'error': error}
                return TemplateResponse(request, 'account/partner/info.html', ctx)
            else:
                return TemplateResponse(request, 'account/partner/step_3.html')

    # GET request
    form, preview = get_address_form(request.POST or None, 'US')
    request.session['email_code'] = random.randint(100000, 999999)
    request.session['email_send'] = 'no'
    request.session['sms_code'] = random.randint(1000, 9999)
    request.session['sms_send'] = 'no'
    ctx = {'form': form}
    return TemplateResponse(request, 'account/partner/step_1.html', ctx)
