from datetime import datetime, timezone
from itertools import groupby


class StripeInvoiceService:
    def __init__(self, upcoming_invoice):
        self._upcoming_invoice = upcoming_invoice

        lines = upcoming_invoice.get("lines")

        if lines.get("has_more") is True:
            self.lines = upcoming_invoice.lines.list(limit=100)
            self.lines = self.lines.get("data", [])
        else:
            self.lines = lines.get("data", [])

        self._selected_keys = [
            "next_payment_attempt",
            "billing_reason",
            "collection_method",
            "customer_email",
            "currency",
            "account_name",
            "subscription_proration_date",
            "status",
            "period_start",
            "period_end",
        ]

        del lines

    def get_common_data(self) -> dict:
        return {
            ele: self._upcoming_invoice[ele]
            for ele in self._upcoming_invoice.keys()
            if ele in self._selected_keys
        }

    @classmethod
    def _parse_currency(cls, value):
        return f"${value}" if value >= 0 else f"- ${value * -1}"

    def get_common_amounts(self) -> dict:
        sub_total = []
        discount_total = []

        for ele in self.lines:
            sub_total.append(ele.get("amount"))
            discount_amounts_in_line = [
                _ele_discount.get("amount")
                for _ele_discount in ele.get("discount_amounts", [])
            ]
            discount_total.extend(discount_amounts_in_line)

        sub_total = sum(sub_total)
        discount_total = sum(discount_total)
        total = sub_total - discount_total

        if total < 0:
            applied_balance = abs(total)
            amount = total + applied_balance
        else:
            applied_balance = 0
            amount = total

        return {
            "lines": self.lines,
            "subtotal": sub_total,
            "discount_total": discount_total,
            "total": total,
            "applied_balance": applied_balance,
            "amount": amount,
        }

    def get_data_lines(self) -> list:
        """
        group by data lines by period
        """
        data = sorted(
            self.lines,
            key=lambda ele: (ele.get("period")["start"], ele.get("period")["end"]),
            reverse=True,
        )
        res_group_period = groupby(
            data,
            key=lambda ele: (ele.get("period")["start"], ele.get("period")["end"]),
        )
        res = []

        for grouped_key, _data in res_group_period:
            parsed_data = []
            parsed_data_discount_amounts = []

            for _ele in _data:
                _amount = _ele["amount"] / 100
                _amount = self._parse_currency(_amount)
                parsed_data.append(
                    {
                        "description": _ele["description"],
                        "amount": _amount,
                        "quantity": _ele["quantity"],
                    }
                )
                parsed_data_discount_amounts = [
                    {
                        "amount": self._parse_currency(
                            (_ele_discount.get("amount", 0)) / 100 * -1
                        ),
                        "description": "Promotion code",
                    }
                    for _ele_discount in _ele.get("discount_amounts", [])
                ]

            _res = {
                "from": datetime.fromtimestamp(grouped_key[0], tz=timezone.utc),
                "to": datetime.fromtimestamp(grouped_key[1], tz=timezone.utc),
                "data": parsed_data,
                "data_discount_amounts": parsed_data_discount_amounts,
            }

            res.append(_res)

        return res

    def output(self):
        return {
            **self.get_common_data(),
            **self.get_common_amounts(),
            "grouped_lines": self.get_data_lines(),
        }
