import logging
from decimal import Decimal
from app.financial.models import SaleItem
from app.financial.variable.job_status import IMPORT_JOB
from app.financial.variable.sale_item import SINGLE_EDIT_JOB, BULK_EDIT_JOB
from app.financial.variable.shipping_cost_source import BULK_EDIT_SOURCE_KEY, IMPORT_SOURCE_KEY, SINGLE_EDIT_SOURCE_KEY

logger = logging.getLogger(__name__)

SHIPPING_COST_USER_ACTION_SOURCES = {
    SINGLE_EDIT_JOB: SINGLE_EDIT_SOURCE_KEY,
    BULK_EDIT_JOB: BULK_EDIT_SOURCE_KEY,
    IMPORT_JOB: IMPORT_SOURCE_KEY
}


def separate_shipping_cost_by_accuracy(client_id: str, instance: SaleItem, value: float, accuracy: int, source: str):
    changes = dict()
    try:
        assert accuracy > 0, f"accuracy must greater than 0"
        assert instance.shipping_cost != value, f"value shipping cost is not change"
        ins_shipping_cost_accuracy = (instance.shipping_cost_accuracy or 0)
        if accuracy <= ins_shipping_cost_accuracy:
            return instance, changes
        instance.shipping_cost = value
        if accuracy < 100:
            estimated_shipping_cost = value
            actual_shipping_cost = None
        else:
            estimated_shipping_cost = instance.estimated_shipping_cost
            actual_shipping_cost = value
        if instance.actual_shipping_cost != actual_shipping_cost:
            changes.update(
                {
                    "actual_shipping_cost": [str(instance.actual_shipping_cost),
                                             Decimal(format(actual_shipping_cost, ".2f"))]
                }
            )
            instance.actual_shipping_cost = actual_shipping_cost
        if instance.estimated_shipping_cost != estimated_shipping_cost:
            changes.update(
                {
                    "estimated_shipping_cost": [str(instance.estimated_shipping_cost),
                                                Decimal(format(estimated_shipping_cost, ".2f"))]
                }
            )
            instance.estimated_shipping_cost = estimated_shipping_cost
        if ins_shipping_cost_accuracy != accuracy:
            changes.update(
                {
                    "shipping_cost_accuracy": [f"{instance.shipping_cost_accuracy}%", f"{accuracy}%"]
                }
            )
            instance.shipping_cost_accuracy = accuracy
        if instance.shipping_cost_source != source:
            changes.update(
                {
                    "shipping_cost_source": [instance.shipping_cost_source, source]
                }
            )
            instance.shipping_cost_source = source
    except Exception as ex:
        logger.debug(f"[{client_id}][separate_shipping_cost_by_accuracy] {ex}")
    return instance, changes


def separate_shipping_cost_by_data(client_id: str, instance: SaleItem, validated_data: dict, job_action: str = None):
    def remove_field_validated_data(fields: [str]):
        try:
            for field in fields:
                if field not in validated_data:
                    continue
                del validated_data[field]
        except Exception as err:
            logger.debug(f"[{client_id}][separate_shipping_cost_by_data][{instance}][{job_action}] {err}")

    def is_has_fields_changed(fields: [str]):
        val = False
        for field in fields:
            try:
                val |= validated_data[field] != (getattr(instance, field) or 0)
            except Exception as err:
                logger.debug(f"[{client_id}][separate_shipping_cost_by_data][{instance}][{job_action}] {err}")
        return val

    try:
        assert is_has_fields_changed(
            ["actual_shipping_cost", "estimated_shipping_cost", "shipping_cost_accuracy"]
        ) is True, f"The asc or esc or accuracy isn't change"
        # accuracy_data = validated_data.get("shipping_cost_accuracy")
        accuracy_ins = getattr(instance, "shipping_cost_accuracy")
        if validated_data.get("shipping_cost_source") is None \
                and ("actual_shipping_cost" in validated_data
                     or ("estimated_shipping_cost" in validated_data and (accuracy_ins or 0) < 100)):
            validated_data.update(
                {"shipping_cost_source": SHIPPING_COST_USER_ACTION_SOURCES.get(job_action, job_action)}
            )
        if (accuracy_ins or 0) == 100 and "actual_shipping_cost" not in validated_data:
            remove_field_validated_data(["shipping_cost_accuracy", "shipping_cost_source"])
        asc = validated_data.get("actual_shipping_cost", getattr(instance, "actual_shipping_cost"))
        esc = validated_data.get("estimated_shipping_cost", getattr(instance, "estimated_shipping_cost"))
        shipping_cost = asc if asc is not None else esc
        if shipping_cost != instance.shipping_cost:
            validated_data.update({"shipping_cost": shipping_cost})
        if "actual_shipping_cost" in validated_data and asc is not None:
            validated_data.update({"shipping_cost_accuracy": 100})
        logger.debug(f"[{client_id}][separate_shipping_cost_by_data][{instance}][{job_action}] {validated_data}")
    except Exception as ex:
        remove_field_validated_data(
            ["actual_shipping_cost", "estimated_shipping_cost", "shipping_cost_accuracy", "shipping_cost_source"]
        )
        logger.debug(f"[{client_id}][separate_shipping_cost_by_data][{instance}][{job_action}] {ex}")
