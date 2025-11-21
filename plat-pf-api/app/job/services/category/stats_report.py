from app.job.services.category.base.job_client import JobClientBase
from app.job.utils.variable import STATS_REPORT_CATEGORY


class StatsReportJob(JobClientBase):
    category = STATS_REPORT_CATEGORY