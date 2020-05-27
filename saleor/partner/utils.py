from .models import Partner, PartnerProductVariant, PartnerProduct, PartnerOrder, PartnerCustomer

def check_partner_url(url_name):
    partner = Partner.objects.filter(url_active=True, url_short=url_name)

    if partner:
        return True

    return False

def get_partner_offer_product(partner_url):

    #products =
    pass


def update_partner(user):

    partner, created = Partner.objects.get_or_create(user=user)

    partner.first_name = user.first_name
    partner.last_name = user.last_name
    partner.phone = user.phone
    partner.billing_address = user.default_billing_address
    partner.save()


def update_partner_variant(user, product, variant):
    partner, created = Partner.objects.get_or_create(user=user)

    partner_variant, created = PartnerProductVariant.objects.get_or_create(partner=partner, product_variant=variant)


def create_partner_order(user, order):
    partner, created = Partner.objects.get_or_create(user=user)

    partner_order, created = PartnerOrder.objects.get_or_create(partner=partner, order=order)
    partner_order.visible = True
    partner_order.can_offer = True
    partner_order.save()

    #check customer


def create_partner_customer(user, customer):
    partner, created = Partner.objects.get_or_create(user=user)
    customer, created = PartnerCustomer.objects.get_or_create(partner=partner, customer=customer)


def handle_partner_order_placement(user, order):
    #when order is placed (payment may not be done

    return link_checkout_order_with_partners(user, order)


def handle_partner_checkout_success(user, order):
    #when user paid order
    #depend on checkout parameter
    return link_checkout_order_with_partners(user, order)


def link_checkout_order_with_partners(user, order):
    #when order is paid

    partners = Partner.objects.all()

    for partner in partners:

        partner_order, created = PartnerOrder.objects.get_or_create(partner=partner, order=order)

        #if exist check if it is Partner own order
        #partner_order.visible = True
        #when to link customer.
        #partner_order.can_offer = True
        #partner_order.save()



#used in product_create, link product with partner, for not-standard products
def create_partner_product(user, product):
    partner, created = Partner.objects.get_or_create(user=user)

    product, created = PartnerProduct.objects.get_or_create(partner=partner, product=product)

    product.is_standard = False
    product.save()