from django.core.management.base import BaseCommand
from django.db import DEFAULT_DB_ALIAS
from django.utils import timezone

from app.financial.jobs.settings import handler_init_client_dashboard_widget
from app.financial.models import DashboardConfig, WidgetConfig, ClientPortal
from app.financial.variable.dashboard import DEFAULT_PROPORTION, HALF_PROPORTION


class Command(BaseCommand):
    help = "Command init dashboard widget data."

    def add_arguments(self, parser):
        parser.add_argument('-over_position', '--override_position', action='store_true',
                            help='Accept/Denied override position exists')
        parser.add_argument('-over_proportion', '--override_proportion', action='store_true',
                            help='Accept/Denied override proportion exists')
        parser.add_argument('-sync', '--sync_clients', action='store_true', help='Accept/Denied override config exists')

    def handle(self, *args, **options):
        override_position = options['override_position']
        override_proportion = options['override_proportion']
        sync_clients = options['sync_clients']

        override_fields = {
            "position": override_position,
            "proportion": override_proportion
        }

        print(f"begin init dashboard widgets .... ")
        #
        dashboards_config = [
            dict(key='overview', value='Overview'),
            dict(key='geographic', value='Geographic Analysis'),
        ]
        #
        widgets_config = {
            'overview': [
                dict(key='dashboard_date', value='Dashboard Date', position=1, proportion=DEFAULT_PROPORTION),
                dict(key='overall_sales', value='Overall Sales', position=2, proportion=DEFAULT_PROPORTION),
                dict(key='sales_by_division', value='Sales by Division', position=3, proportion=DEFAULT_PROPORTION),
                dict(key='sales_by_asin', value='Sales By ASIN', position=4, proportion=DEFAULT_PROPORTION),
                dict(key='big_moves', value='Big Moves', position=5, proportion=DEFAULT_PROPORTION),
                dict(key='all_sales_comparison', value='All Sales Comparison', position=6,
                     proportion=DEFAULT_PROPORTION),
                dict(key='total_sales_tracker', value='Total Sales Tracker', position=7, proportion=DEFAULT_PROPORTION),
                dict(key='broken_down_sales', value='Broken Down Sales', position=8, proportion=DEFAULT_PROPORTION),
                dict(key='p_&_l', value='P&L', position=9, proportion=DEFAULT_PROPORTION),
                dict(key='ordered_product_sales', value='Ordered Product Sales', position=10,
                     proportion=HALF_PROPORTION),
                dict(key='yoy_monthly_sales', value='YOY Monthly Sales', position=11, proportion=HALF_PROPORTION),
                dict(key='view_comparison_tag', value='View Comparison Tag', position=12,
                     proportion=DEFAULT_PROPORTION),
                dict(key='top_product_performance', value='Top Product Performance Last 30 Days', position=13,
                     proportion=DEFAULT_PROPORTION),
                dict(key='sale_by_dollar', value='Sale By $ Amount', position=14, proportion=DEFAULT_PROPORTION),
                dict(key='all_sales', value='All Sales', position=15, proportion=DEFAULT_PROPORTION),
                dict(key='30_day_sales', value='30 Day Sales ($)', position=16, proportion=HALF_PROPORTION),
                dict(key='30_day_sales_brand', value='30 Day Sales ($) (Brand)', position=17,
                     proportion=HALF_PROPORTION),
                dict(key='all_sales_last_30_days', value='All Orders (Last 30 Days)', position=18,
                     proportion=HALF_PROPORTION),
                dict(key='all_sales_last_20_months', value='All Orders (Last 20 Months)', position=19,
                     proportion=HALF_PROPORTION),
                dict(key='top_performing_styles', value='Top Performing Styles', position=20,
                     proportion=DEFAULT_PROPORTION)
            ],
            'geographic': [
                dict(key='global_filter', value='Global filter', position=1, proportion=DEFAULT_PROPORTION),
                dict(key='sales_per_state', value='Sales per State', position=2, proportion=DEFAULT_PROPORTION),
                dict(key='heat_map_summary', value='Heat Map Summary', position=3, proportion=DEFAULT_PROPORTION),
            ]
        }

        dashboards_objs = []
        widgets_objs_insert = []
        widgets_objs_update = []

        for item in dashboards_config:
            dashboard_key = item['key']
            try:
                dash_obj = DashboardConfig.objects.get(key=dashboard_key)
            except Exception as ex:
                dash_obj = DashboardConfig(**item)
                dashboards_objs.append(dash_obj)

            widgets = widgets_config[dashboard_key]

            for widget in widgets:
                widget_key = widget['key']
                try:
                    widget_obj = WidgetConfig.objects.get(dashboard_id=dash_obj.pk, key=widget_key)
                    if not override_proportion and not override_proportion:
                        continue
                    for k, v in widget.items():
                        if k not in override_fields:
                            continue
                        if override_fields[k] is True:
                            setattr(widget_obj, k, v)
                    widget_obj.modified = timezone.now()
                    widgets_objs_update.append(widget_obj)  # update
                except Exception as ex:
                    widget_obj = WidgetConfig(dashboard_id=dash_obj.pk, **widget)
                    widgets_objs_insert.append(widget_obj)

        if dashboards_objs:
            DashboardConfig.objects.tenant_db_for(DEFAULT_DB_ALIAS).bulk_create(dashboards_objs, ignore_conflicts=True)

        if widgets_objs_insert:
            WidgetConfig.objects.tenant_db_for(DEFAULT_DB_ALIAS).bulk_create(widgets_objs_insert, ignore_conflicts=True)

        if widgets_objs_update:
            WidgetConfig.objects.tenant_db_for(DEFAULT_DB_ALIAS) \
                .bulk_update(widgets_objs_update, fields=['icon_url', 'position', 'proportion', 'modified'])

        if sync_clients:
            print(f"begin init clients dashboard widgets .... ")

            client_ids = ClientPortal.objects.tenant_db_for(DEFAULT_DB_ALIAS).values_list('pk', flat=True)

            handler_init_client_dashboard_widget(client_ids=client_ids, override_position=override_position,
                                                 override_proportion=override_proportion)

        print(f"End init dashboard widgets .... ")
