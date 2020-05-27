from django.contrib import admin
from ..account.models import User
from django.contrib.admin import AdminSite
from .models import Partner, PartnerOrder, PartnerProduct, PartnerProductVariant, PartnerFulfillment, PartnerFulfillmentLine

class AXCAdminSite(AdminSite):
    site_header = 'AXC administration'

admin_site = AXCAdminSite(name='myadmin')
admin_site.register(User)
admin_site.register(Partner)
admin_site.register(PartnerProduct)
admin_site.register(PartnerOrder)
admin_site.register(PartnerProductVariant)
admin_site.register(PartnerFulfillment)
admin_site.register(PartnerFulfillmentLine)
