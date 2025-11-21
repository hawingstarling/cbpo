from app.job.services.category.base.job_client import JobClientBase
from app.job.utils.variable import DATA_SOURCE_CALCULATION_CATEGORY


class DataSourceCalculationJob(JobClientBase):
    category = DATA_SOURCE_CALCULATION_CATEGORY
