from app.job.services.category.base.job_client import JobClientBase
from app.job.utils.variable import SYNC_ANALYSIS_CATEGORY


class SyncAnalysisJob(JobClientBase):
    category = SYNC_ANALYSIS_CATEGORY
