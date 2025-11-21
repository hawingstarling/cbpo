from django.urls import path

from ..sub_views.user import (CheckUserExistedView, ClientUserBelongView, NumberNewNotificationView, ListNotificationView,
                              UpdateNotificationStatusView,
                              UpdateNotificationIsSeenView, UserAllClientSettingDataView,
                              UpdateNotificationIsSeenDeclineView)

urlpatterns = [

    path('user/clients/',
         ClientUserBelongView.as_view(),
         name='clients-user-belong'),
    path('user/clients/all-settings-data/',
         UserAllClientSettingDataView.as_view(),
         name='clients-user-all-settings'),

    path('user/notification/new/',
         NumberNewNotificationView.as_view(),
         name='user-notification-new'),

    path('user/notification/',
         ListNotificationView.as_view(),
         name='user-notification-list'),

    path('user/notification/<uuid:notification_id>/is-seen/',
         UpdateNotificationIsSeenView.as_view(),
         name='user-notification-update-is-seen'),

    path('user/notification/<uuid:notification_id>/is-seen/decline/',
         UpdateNotificationIsSeenDeclineView.as_view(),
         name='user-notification-update-is-seen-denied'),

    path('user/notification/<uuid:notification_id>/status/',
         UpdateNotificationStatusView.as_view(),
         name='user-notification-update-status'),
    
    path('user/is-existed/',
         CheckUserExistedView.as_view(),
         name='check-user-is-existed')
]
