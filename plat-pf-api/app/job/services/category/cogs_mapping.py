from app.job.services.category.base.job_client import JobClientBase
from app.job.utils.variable import COGS_MAPPING_CATEGORY


class COGSMappingJob(JobClientBase):
    category = COGS_MAPPING_CATEGORY
