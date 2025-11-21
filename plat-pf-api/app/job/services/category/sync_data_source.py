from app.job.services.category.base.job_client import JobClientBase
from app.job.utils.variable import SYNC_DATA_SOURCE_CATEGORY


class SyncDataSourceJob(JobClientBase):
    category = SYNC_DATA_SOURCE_CATEGORY
