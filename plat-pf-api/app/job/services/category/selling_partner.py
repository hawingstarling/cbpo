from app.job.services.category.base.job_client import JobClientBase
from app.job.utils.variable import SELLING_PARTNER_CATEGORY


class SellingPartnerJob(JobClientBase):
    category = SELLING_PARTNER_CATEGORY
