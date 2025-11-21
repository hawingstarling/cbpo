import uuid
from django.db.utils import DEFAULT_DB_ALIAS
from app.financial.models import ClientPortal
from app.job.models import CommunityJobClient
from app.job.utils.helper import get_category_services_config
from app.job.utils.variable import COMMUNITY_CATEGORY


def request_to_ping():
    client_id = ClientPortal.objects.tenant_db_for(DEFAULT_DB_ALIAS).first().pk
    pk = uuid.uuid4()
    obj = CommunityJobClient(
        name='job_ping_request',
        client_id=client_id,
        job_name='app.job.utils.trigger.job_ping_request',
        module='app.job.utils.trigger',
        method='job_ping_request',
        meta=dict(category=COMMUNITY_CATEGORY)
    )
    obj.pk = pk
    CommunityJobClient.objects.tenant_db_for(DEFAULT_DB_ALIAS).bulk_create([obj])
    get_category_services_config()[COMMUNITY_CATEGORY]().on_validate().on_process().on_complete()
    print(f"[request_to_ping] {obj}")
