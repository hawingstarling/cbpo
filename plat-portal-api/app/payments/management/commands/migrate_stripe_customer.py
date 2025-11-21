from django.core.management import BaseCommand
from datetime import datetime, timezone

from app.core.logger import logger

from app.tenancies.models import User

from app.payments.stripe_configured import stripe_configured
from app.payments.models import StripeCustomer, Subscription


class Command(BaseCommand):
    args = "<foo bar ...>"
    help = "our help string comes here"

    """
    migrate Customer from Stripe
    """

    def handle(self, *args, **options):
        customers = stripe_configured.Customer.list(limit=100).get("data")

        stripe_subscriptions = stripe_configured.Subscription.list(limit=100).get(
            "data"
        )

        local_subsriptions = Subscription.objects.all().select_related("user")

        for _ele_sub in local_subsriptions:
            find_stripe_sub = filter(
                lambda ele: _ele_sub.external_subscription_id == ele.get("id"),
                stripe_subscriptions,
            )
            try:
                _sub = next(find_stripe_sub)
            except StopIteration:
                print(f"subscription {_ele_sub.external_subscription_id}")
                continue

            # Finding in list of Stripe Customers
            find_customer = filter(
                lambda ele: ele.get("id") == _sub.get("customer"), customers
            )

            find_customer = list(find_customer)[0]

            user = User.objects.get(email=find_customer.get("email"))

            StripeCustomer.all_objects.update_or_create(
                user=user,
                defaults={
                    "is_removed": False,
                    "customer_stripe_id": find_customer.get("id"),
                },
            )

        len_local_customer = StripeCustomer.objects.all().count()
        len_stripe_customer = len(customers)

        logger.info(f"number of local stripe customer: {len_local_customer}")
        logger.info(f"number of stripe customer: {len_stripe_customer}")

    def protation(self, *args, **kwargs):
        """
        grade changes and protation calculation
        explaination
        """
        start = 1618309869
        end = 1620901869

        time_delta = end - start

        logger.info(f"period start {datetime.fromtimestamp(start, tz=timezone.utc)}")
        logger.info(f"period end {datetime.fromtimestamp(end, tz=timezone.utc)}")

        logger.info(f"time delta = {end - start}")

        mmm = datetime.fromtimestamp(end, tz=timezone.utc) - datetime.fromtimestamp(
            start, tz=timezone.utc
        )
        print(mmm.total_seconds())
        print(mmm.total_seconds() / 60)

        current_price_the_plan = 999
        logger.info(f"current_price_the_plan = ${current_price_the_plan}")
        _avg = current_price_the_plan / time_delta

        logger.info(f"avg = {_avg}")

        current = datetime.now(tz=timezone.utc).timestamp()
        current = int(current)

        unused_time = end - current

        logger.info(f"unused time on the old plan = ${_avg * unused_time}")

        price_the_new_plan = 499
        _avg_on_the_new = price_the_new_plan / time_delta

        logger.info(f"remaining on the new plan = ${_avg_on_the_new * unused_time}")
