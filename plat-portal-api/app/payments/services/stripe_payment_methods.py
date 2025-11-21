from app.payments.services.utils import StripeApiServices


class StripePaymentMethods:
    """
    get all payment method from a stripe customer
    """

    def __init__(self, stripe_customer_id: str):
        payment_methods = StripeApiServices.get_payment_methods(stripe_customer_id)

        self.payment_methods = payment_methods.get("data", [])
        self.including_keys = [
            "brand",
            "country",
            "exp_month",
            "exp_year",
            "last4",
        ]

    def get_all(self) -> list:
        return self._extract_data(self.payment_methods)

    def get_latest(self) -> list:
        # first one is the current payment method
        list_of_latest_method = self.payment_methods[:1]
        return self._extract_data(list_of_latest_method)

    def _extract_data(self, list_of_methods: list) -> list:
        parsed_payment_methods = []
        for ele in list_of_methods:
            card = ele.get("card")
            card = {key: card[key] for key in card if key in self.including_keys}
            _res = {
                "billing_details": ele.get("billing_details"),
                "type": ele.get("type"),
                "card": card,
                "id": ele.get("id"),
            }
            parsed_payment_methods.append(_res)

        return parsed_payment_methods
