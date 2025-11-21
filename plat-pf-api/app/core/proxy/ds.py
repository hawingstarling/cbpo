import copy
import json, logging, pytz
from revproxy.views import ProxyView
from app.core.services.user_permission import get_user_permission
from app.core.variable.marketplace import CHANNEL_DEFAULT
from config.settings.common import DS_EXPORT_LIMIT
from app.core.context import AppContext
from app.core.exceptions import AnalysisDataException, NotWorkspaceDSException
from app.core.variable.permission import ROLE_ADMIN, ROLE_OWNER
from app.core.proxy.base import BaseCustomProxyView
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DSProxyView(BaseCustomProxyView):
    column_filter = 'sale_date'

    def __init__(self, *args, **kwargs):
        super(BaseCustomProxyView, self).__init__(*args, **kwargs)

        self.channel_name = None

    def verify_extension(self, request):
        client_id = request.META.get('HTTP_X_PS_CLIENT_ID', None)
        if not client_id:
            raise NotWorkspaceDSException()

    def handler_request_body(self, request):
        """
        This is method custom for verify authentication/authorization to DS
            1. get jwt of request proxy
            2. call service integrate with portal check permission of client user
            3. If fail raise exception or return list empty
        :param request:
        :return:
        """
        logger.info("upstream : {}".format(self.upstream))
        # get info of client
        context = AppContext.instance()
        # check permission and handel view data
        self.verify_user_permission(jwt_token=context.jwt_token, client_id=context.client_id, user_id=context.user_id)

    def verify_user_permission(self, jwt_token: str = None, user_id: str = None, client_id: str = None):
        user_permission = get_user_permission(jwt_token, client_id, user_id)
        permissions = user_permission.permissions
        self.modify_general_request()
        if user_permission.role in [ROLE_ADMIN, ROLE_OWNER] or permissions['SALE_VIEW_ALL']:
            return True
        if permissions['SALE_VIEW_24H']:
            self.modify_body_for_staff()
            return True
        raise AnalysisDataException(verbose=True)

    @property
    def proxy_should_be_modified(self) -> bool:
        """
        check proxy request
        :return:
        """
        path: str = self.request.resolver_match.kwargs.get('path', None)
        prefix_required = 'v1/ds/'
        if not path.startswith(prefix_required):
            return False
        postfix_required = ['/exec', '/count']
        for e in postfix_required:
            if path.endswith(e):
                return True
        return False

    def modify_body_for_staff(self):
        """
        append json condition to DS request
        limit time range for 24 hours based on 'created' field
        :return:
        """

        body = None
        try:
            body = json.loads(self.request.body)
        except ValueError:
            body = None

        # case 1: body is empty
        if body is None:
            body = {
                "query": {
                    "filter": self.build_condition_for_24_hours
                }
            }
            self.request._body = json.dumps(body)
            return
        # case 2: filter is empty
        query = copy.deepcopy(body.get('query'))
        fil = query.get('filter', None)
        if fil is None:
            fil = {
                "filter": self.build_condition_for_24_hours
            }
            body['query'].update(fil)
            self.request._body = json.dumps(body)
            return
        # case 3: filter exist -> append conditions
        conditions = fil.get('conditions', [])
        self.channel_name = self.__find_channel_name(conditions)
        fil = {
            "type": "AND",
            "conditions": [fil, self.build_condition_for_24_hours]
        }
        query.update({'filter': fil})
        body['query'].update(query)
        self.request._body = json.dumps(body)
        return

    def __find_channel_name(self, conditions: list = []):
        channel_name = None

        if not isinstance(conditions, list):
            return channel_name

        for item in conditions:
            try:
                if 'conditions' in item and isinstance(item['conditions'], list):
                    channel_name = self.__find_channel_name(item['conditions'])
                    if channel_name is not None:
                        return channel_name
                if item.get('column', None) == 'channel_name':
                    channel_name = item.get('value')
                    return channel_name
            except Exception as ex:
                logger.error(f'[{self.__class__.__name__}][handler_filter_condition_query][conditions]: {conditions}')
                logger.error(f'[{self.__class__.__name__}][handler_filter_condition_query]: {ex}')
                continue

        return channel_name

    @property
    def build_condition_for_24_hours(self):
        if self.channel_name is None:
            self.channel_name = CHANNEL_DEFAULT
        time_now = datetime.now(tz=pytz.utc)
        time_last_24h = time_now - timedelta(days=1)

        return {
            "type": "AND",
            'conditions': [
                {
                    "column": 'channel_name',
                    "value": self.channel_name,
                    "operator": "$eq",
                },
                {
                    "column": self.column_filter,
                    "value": time_last_24h.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    "operator": "$gte",
                },
                {
                    "column": self.column_filter,
                    "value": time_now.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    "operator": "$lte",
                }
            ]
        }

    def modify_general_request(self):
        path: str = self.request.resolver_match.kwargs.get('path', None)
        # Modify ds-export limit
        if path.endswith('/export'):
            self.request.GET._mutable = True
            self.request.GET['limit'] = DS_EXPORT_LIMIT


class PingDSProxyView(ProxyView):
    def dispatch(self, request):
        path = 'ping'
        return super().dispatch(request, path)
