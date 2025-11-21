import asyncio

from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

from app.core.services_status import checking_status

# Create your views here.


class CheckServicesStatusView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(tags=["Services status"])
    def get(self, request, *args, **kwargs):
        res = asyncio.run(checking_status())
        return Response(res, status=HTTP_200_OK)
