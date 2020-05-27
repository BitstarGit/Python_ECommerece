import json

from django.contrib import messages
from django.template.response import TemplateResponse
from django.utils.translation import pgettext_lazy
from draftjs_sanitizer import SafeJSONEncoder
from impersonate.views import impersonate as orig_impersonate
from django.http import HttpResponse, HttpResponseNotFound, Http404,  HttpResponseRedirect
from ..account.models import User

from datetime import date, timedelta
from django.conf import settings
from ..product.utils import products_for_homepage, product_for_partner_homepage
from ..product.utils.availability import products_with_availability
from ..seo.schema.webpage import get_webpage_schema
from ..partner.utils import check_partner_url

def home(request):

    cookie_name = request.get_signed_cookie("partner", "")

    if cookie_name:
        products = product_for_partner_homepage(cookie_name)
    else:
        products = products_for_homepage(
            request.user, request.site.settings.homepage_collection
        )[:8]

    products = list(
        products_with_availability(
            products,
            discounts=request.discounts,
            country=request.country,
            local_currency=request.currency,
            extensions=request.extensions,
        )
    )
    webpage_schema = get_webpage_schema(request)
    return TemplateResponse(
        request,
        "home.html",
        {
            "parent": None,
            "products": products,
            "webpage_schema": json.dumps(webpage_schema, cls=SafeJSONEncoder),
        },
    )


def styleguide(request):
    return TemplateResponse(request, "styleguide.html")


def instagram(request):
    return HttpResponseRedirect(settings.INST_LINK)


def facebook(request):
    return HttpResponseRedirect(settings.FACE_LINK)


def about_us(request):
    return TemplateResponse(request, "about.html")


def for_partners(request):
    return TemplateResponse(request, "partners.html")


def resolve_url(request, username):

    max_age = int(timedelta(days=30).total_seconds())
    partner_check = check_partner_url(username)

    if partner_check :
        response = home(request)
        response.set_signed_cookie("partner", username, max_age=max_age)
    else:
        response = handle_404(request)

    return response

def impersonate(request, uid):
    response = orig_impersonate(request, uid)
    if request.session.modified:
        msg = pgettext_lazy(
            "Impersonation message",
            "You are now logged as {}".format(User.objects.get(pk=uid)),
        )
        messages.success(request, msg)
    return response


def handle_404(request, exception=None):
    return TemplateResponse(request, "404.html", status=404)


def manifest(request):
    return TemplateResponse(request, "manifest.json", content_type="application/json")
