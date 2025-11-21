import hashlib
import json
from datetime import datetime

import maya
from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from app.financial.models import DataFeedTrack, Brand, Channel
from app.core.permissions.base import InternalPermission
from app.financial.sub_serializers.data_feed_serializer import DataFeedRetrieveSerializer
from django.utils import timezone
from app.financial.variable.data_feed import DATA_FEED_TYPE_LIST, FEED_ACTION_SCHEDULER, FEED_ACTION_ON_DEMAND
from app.financial.variable.data_flatten_variable import FLATTEN_SALE_ITEM_KEY, FLATTEN_YOY_30_DAY_SALE_KEY
from app.job.utils.helper import register
from app.job.utils.variable import SYNC_DATA_SOURCE_CATEGORY, MODE_RUN_IMMEDIATELY


class DataFeedRetrieveView(APIView):
    serializer_class = DataFeedRetrieveSerializer
    permission_classes = (InternalPermission,)
    channel = openapi.Parameter('channel', in_=openapi.IN_QUERY,
                                description="Channel name",
                                type=openapi.TYPE_STRING,
                                required=False)
    brands = openapi.Parameter('brands', in_=openapi.IN_QUERY,
                               description="Brand names",
                               type=openapi.TYPE_ARRAY,
                               items=openapi.Items(type=openapi.TYPE_STRING),
                               required=True)

    from_date = openapi.Parameter('from', in_=openapi.IN_QUERY,
                                  description="From Date",
                                  type=openapi.TYPE_STRING,
                                  required=False)

    to_date = openapi.Parameter('to', in_=openapi.IN_QUERY,
                                description="To Date",
                                type=openapi.TYPE_STRING,
                                required=False)

    feed_type = openapi.Parameter('feed_type', in_=openapi.IN_QUERY,
                                  description="Feed Type",
                                  type=openapi.TYPE_STRING,
                                  required=False)

    @swagger_auto_schema(manual_parameters=[channel, brands, from_date, to_date, feed_type])
    def get(self, request, *args, **kwargs):

        client_id = kwargs.get('client_id')
        brands = request.query_params.get('brands').split(',')
        cond = Q(
            client_id=client_id, brand__name__in=brands,
            latest=True
        )
        channel = request.query_params.get('channel')
        if channel:
            cond &= Q(channel__name=channel)

        from_date = request.query_params.get('from', None)
        to_date = request.query_params.get('to', None)

        if not from_date and not to_date:
            now = timezone.now()
            cond &= Q(action=FEED_ACTION_SCHEDULER, date__year=now.year)
        else:
            cond &= Q(action=FEED_ACTION_ON_DEMAND)
            if from_date:
                cond &= Q(date__gte=from_date)
            if to_date:
                cond &= Q(date__lte=to_date)

        feed_type = request.query_params.get('feed_type', None)
        if feed_type and feed_type in DATA_FEED_TYPE_LIST:
            cond &= Q(type=feed_type)
        else:
            cond &= Q(type=FLATTEN_SALE_ITEM_KEY)

        query_set = DataFeedTrack.objects.tenant_db_for(client_id).filter(cond).order_by('-date')

        items = [{'date': datetime.combine(item.date, datetime.min.time()), 'file_uri': item.file_uri} for item in
                 query_set]
        data = {'items': items}

        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)


class DataFeedForceRunView(DataFeedRetrieveView):
    from_date = openapi.Parameter('from', in_=openapi.IN_QUERY,
                                  description="From Date",
                                  type=openapi.TYPE_STRING,
                                  required=True)

    to_date = openapi.Parameter('to', in_=openapi.IN_QUERY,
                                description="To Date",
                                type=openapi.TYPE_STRING,
                                required=True)

    @swagger_auto_schema(
        manual_parameters=[DataFeedRetrieveView.channel, DataFeedRetrieveView.brands, from_date, to_date,
                           DataFeedRetrieveView.feed_type])
    def get(self, request, *args, **kwargs):
        from_date = request.query_params.get('from')
        to_date = request.query_params.get('to')
        assert maya.parse(from_date).datetime() <= maya.parse(to_date).datetime(), "From/To Date is not valid"
        client_id = kwargs.get('client_id')
        meta = dict(
            client_id=client_id,
            from_date=from_date,
            to_date=to_date
        )
        brands = request.query_params.get('brands').split(',')
        if brands:
            brand_ids = list(
                Brand.objects.tenant_db_for(client_id).filter(client_id=client_id, name__in=brands)
                .values_list('pk', flat=True))
            assert len(brands) > 0, "Brands not found"
            meta.update(dict(brand_ids=brand_ids))
        channel = request.query_params.get('channel')
        if channel:
            channel_ins = Channel.objects.tenant_db_for(client_id).get(name=channel)
            channel_ids = [str(channel_ins.pk)]
            meta.update(dict(channel_ids=channel_ids))
        feed_type = request.query_params.get('feed_type')
        hash_data = hashlib.md5(json.dumps(meta).encode('utf-8')).hexdigest()[:8]
        if feed_type is None:
            feed_type = FLATTEN_SALE_ITEM_KEY
        kwargs = {
            FLATTEN_SALE_ITEM_KEY: dict(
                name=f"force_run_sale_items_data_feed_from_{from_date}_to_{to_date}_{hash_data}",
                job_name="app.financial.jobs.data_feed.handler_auto_generate_sale_items_data_feed",
                module="app.financial.jobs.data_feed",
                method="handler_auto_generate_sale_items_data_feed"
            ),
            FLATTEN_YOY_30_DAY_SALE_KEY: dict(
                name=f"force_run_yoy_30d_sales_data_feed_from_{from_date}_to_{to_date}_{hash_data}",
                job_name="app.financial.jobs.data_feed.handler_auto_generate_yoy_30d_sales_data_feed",
                module="app.financial.jobs.data_feed",
                method="handler_auto_generate_yoy_30d_sales_data_feed"
            )
        }
        register(SYNC_DATA_SOURCE_CATEGORY, client_id, mode_run=MODE_RUN_IMMEDIATELY, meta=meta, **kwargs[feed_type])
        return Response(status=status.HTTP_200_OK)
