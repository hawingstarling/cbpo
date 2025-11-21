from app.job.services.category.base.job_client import JobClientBase
from app.job.utils.variable import BULK_CATEGORY


class BulkJob(JobClientBase):
    category = BULK_CATEGORY
