
from django.core.management.base import BaseCommand
from saleor.order.models import Order, Fulfillment
from saleor.payment.models import Payment, Transaction
from saleor.checkout.models import Checkout

class Command(BaseCommand):
    help = "Populate database with test objects"

    def add_arguments(self, parser):
        parser.add_argument(
            "--orders",
            action="store_true",
            dest="orders",
            default=False,
            help="Delete orders",
        )

    def handle(self, *args, **options):
        self.stdout.write("Delete objects")

        if options["orders"]:
            Transaction.objects.all().delete()
            Payment.objects.all().delete()

            Fulfillment.objects.all().delete()
            Checkout.objects.all().delete()
            Order.objects.all().delete()