from typing import Union

from app.core.logger import logger
from app.payments.config import PLAN_CUSTOM_ON_DEMAND
from app.payments.models import MapWatcherConfigOnDemand, Plan
from app.payments.services.utils import StripeApiServices


class OnDemandPlan:

    demand_config: Union[MapWatcherConfigOnDemand]

    def __init__(self, demand_config_id: str):
        try:
            self.demand_config = MapWatcherConfigOnDemand.objects.get(
                id=demand_config_id
            )
        except Exception as err:
            logger.error(f"{self.__class__.__name__} {err}")
            raise err

    def create(self):
        external_plan_id = self._create_stripe_product()
        plan = self._create_plan_on_system(external_plan_id=external_plan_id)

        self.demand_config.plan = plan
        self.demand_config.is_created_on_stripe = True
        self.demand_config.save(update_fields=["plan", "is_created_on_stripe"])

    def _create_stripe_product(self) -> str:
        try:
            return StripeApiServices.create_product(
                # dollar -> cent
                amount=int(self.demand_config.price * 100),
                name=self.demand_config.name,
            )
        except Exception as err:
            logger.error(f"{self.__class__.__name__} {err}")
            raise err

    def _create_plan_on_system(self, external_plan_id: str) -> Plan:
        try:
            plan = Plan.objects.create(
                application=self.demand_config.application,
                name=self.demand_config.name,
                type=PLAN_CUSTOM_ON_DEMAND,
                period="monthly",
                price=self.demand_config.price,
                external_plan_id=external_plan_id,
                max_workspaces=self.demand_config.tenancy_on_demand["max_workspaces"],
                max_internal_users=self.demand_config.tenancy_on_demand[
                    "max_internal_users"
                ],
                max_external_users=self.demand_config.tenancy_on_demand[
                    "max_external_users"
                ],
                enabled=True,
                trial_days=self.demand_config.trial_days
            )
            return plan
        except Exception as err:
            logger.error(f"{self.__class__.__name__} {err}")
            raise err
