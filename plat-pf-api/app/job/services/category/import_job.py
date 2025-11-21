from app.job.services.category.base.job_client import JobClientBase
from app.job.utils.variable import IMPORT_CATEGORY


class ImportJob(JobClientBase):
    category = IMPORT_CATEGORY