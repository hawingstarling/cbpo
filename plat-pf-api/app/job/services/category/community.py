from app.job.services.category.base.job_client import JobClientBase
from app.job.utils.variable import COMMUNITY_CATEGORY


class CommunityJob(JobClientBase):
    category = COMMUNITY_CATEGORY
