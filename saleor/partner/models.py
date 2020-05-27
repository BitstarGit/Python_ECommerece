
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumber, PhoneNumberField
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    Permission,
    PermissionsMixin,
)
from django.utils.timezone import now
from django.db import models
from django.core.validators import MinValueValidator
from ..account.models import PossiblePhoneNumberField, Address
from ..product.models import ProductVariant, Product
from ..order.models import Order, Fulfillment, FulfillmentLine
from ..account.models import User
from ..checkout.models import Checkout
from ..core.models import SortableModel
from decimal import Decimal
from django_prices.models import MoneyField, TaxedMoneyField

class Partner(models.Model):
    first_name = models.CharField(max_length=256, blank=True)
    last_name = models.CharField(max_length=256, blank=True)
    tax_number = models.CharField(max_length=100, blank=True)
    phone = PossiblePhoneNumberField(blank=True, default="")

    url_short = models.CharField(max_length=50, blank=True)
    url_active = models.BooleanField(default=False)

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    billing_address = models.ForeignKey(
        Address, related_name="+", null=True, blank=True, on_delete=models.SET_NULL
    )

    can_add_product = models.BooleanField(default=False)
    can_add_order = models.BooleanField(default=False)
    can_see_orders = models.BooleanField(default=True)
    can_fulfill_orders = models.BooleanField(default=False)
    can_see_dashboard = models.BooleanField(default=True)
    can_add_customer = models.BooleanField(default=False)
    can_see_customers = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email


class PartnerProductVariant(models.Model):
    partner = models.ForeignKey(
        Partner, related_name="partner_product_variants", on_delete=models.CASCADE
    )

    product_variant = models.ForeignKey(
        ProductVariant, related_name="partner_variants", on_delete=models.CASCADE
    )

    variant_available = models.BooleanField(default=False)
    variant_stock_qty = models.IntegerField(
        validators=[MinValueValidator(0)], default=Decimal(1)
    )


class PartnerOrder(models.Model):
    partner = models.ForeignKey(
        Partner, related_name="partner_orders", on_delete=models.CASCADE
    )

    order = models.ForeignKey(
        Order, related_name="orders_partner", on_delete=models.CASCADE
    )

    visible = models.BooleanField(default=True)
    can_fulfill = models.BooleanField(default=True)
    can_offer = models.BooleanField(default=True)

    def __str__(self):
        return "Order #%d Partner %s" % (self.order.id, self.partner.user.email)


class PartnerProduct(models.Model):
    partner = models.ForeignKey(
        Partner, related_name="products_partner", on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        Product, related_name="partner_products", on_delete=models.CASCADE
    )

    visible = models.BooleanField(default=True)

    def __str__(self):
        return "#%d %s Partner %s" % (self.product.id, self.product.name, self.partner.user.email)


class PartnerCustomer(models.Model):
    partner = models.ForeignKey(
        Partner, related_name="customer_partner", on_delete=models.CASCADE
    )

    customer = models.ForeignKey(
        User, related_name="partner_customer", on_delete=models.CASCADE
    )

    visible = models.BooleanField(default=True)

#partner fulfillment
class PartnerFulfillment(models.Model):
    fulfillment = models.ForeignKey(
        Fulfillment, related_name="partnerfulfillments", editable=False, on_delete=models.CASCADE
    )
    partner = models.ForeignKey(
        Partner, related_name="partnerfulfillments", editable=False, on_delete=models.CASCADE
    )
    partner_status = models.CharField(max_length=32)
    amount = models.CharField(max_length=32)  
    est_shipping_date = models.DateTimeField(default=now)
    
    def get_date(self):
        return self.est_shipping_date
    

#partner fulfillmentline
class PartnerFulfillmentLine(models.Model):
    fulfillment_line = models.ForeignKey(
        FulfillmentLine, related_name="partner_lines", on_delete=models.CASCADE
    )
    unit_price = models.CharField(max_length=255, default="", blank=True)
    line_status = models.CharField(max_length=255, default="", blank=True)

#checkout extension
class PartnerCheckout(models.Model):
    checkout = models.ForeignKey(
        Checkout, related_name="ext", on_delete=models.CASCADE
    )

    can_collect = models.BooleanField(default=True)
    can_publish = models.BooleanField(default=True)
    order_expiry_days = models.IntegerField(default=7)


class PartnerPoint(SortableModel):
    partner = models.ForeignKey(
        Partner, related_name="points", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    active = models.BooleanField(default=False)
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    long = models.DecimalField(max_digits=9, decimal_places=6)

    point_address = models.ForeignKey(
        Address, related_name="partner_points", null=True, on_delete=models.SET_NULL
    )

    class Meta:
        ordering = ("sort_order",)
