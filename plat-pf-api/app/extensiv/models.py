import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models
from model_utils.models import TimeStampedModel

from app.database.db.dynamic_models.cogs_conflict import COGSConflictMultiTblManager
from app.extensiv.variables import ConflictStatus, COGSourceSystem


class COGSConflict(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(
        "financial.ClientPortal", on_delete=models.CASCADE)
    channel = models.ForeignKey("financial.Channel", on_delete=models.CASCADE)
    sku = models.CharField(max_length=100, db_index=True)
    sale_ids = ArrayField(
        base_field=models.CharField(max_length=50),
        blank=True,
        default=list,
        help_text="List of sale IDs (as strings) related to this conflict."
    )
    channel_sale_ids = ArrayField(
        base_field=models.CharField(max_length=50),
        blank=True,
        default=list,
        help_text="List of sale IDs (as strings) related to this conflict."
    )

    extensiv_cog = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True,
                                       verbose_name='Extensiv COGs')
    dc_cog = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True,
                                 verbose_name='Data Central COGs')
    pf_cog = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True,
                                 verbose_name='PF COGs')

    used_cog = models.CharField(max_length=20, choices=COGSourceSystem.choices)

    status = models.CharField(
        max_length=20, choices=ConflictStatus.choices, default=ConflictStatus.CONFLICT)

    note = models.TextField(blank=True, default="")

    #
    objects = COGSConflictMultiTblManager()
    all_objects = COGSConflictMultiTblManager()

    class Meta:
        indexes = [
            models.Index(fields=["sku", "status"]),
        ]

    def __str__(self):
        return f"COGS Conflict for SKU {self.sku} (Sale #{self.sale_ids})"

    def recalculate_status(self):
        """
        Tính lại status dựa trên tất cả các giá trị COG hiện có.
        Cập nhật status của instance này.
        """
        self.status = calculate_conflict_status(
            extensiv_cog=self.extensiv_cog,
            dc_cog=self.dc_cog,
            pf_cog=self.pf_cog
        )
        return self.status

    def difference(self):
        """Return the absolute difference in COGS."""
        if self.extensiv_cog is not None and self.dc_cog is not None:
            return abs(self.extensiv_cog - self.dc_cog)
        return None

# class ExtensivProductCache(TimeStampedModel):
#     sku = models.CharField(max_length=100, unique=True, db_index=True)
#     vendor_cost = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
#     default_vendor_id = models.CharField(max_length=50, blank=True, null=True)
#     response_hash = models.CharField(max_length=64, blank=True, null=True)
#     raw_response = models.JSONField(blank=True, null=True)
#     last_fetched_at = models.DateTimeField(auto_now=True)
#     expires_at = models.DateTimeField(null=True, blank=True)  # optional TTL if needed
#
#     class Meta:
#         indexes = [models.Index(fields=["sku", "last_fetched_at"])]
#
#     def __str__(self):
#         return f"Extensiv Cache for {self.sku}"
