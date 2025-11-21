from django.db.models import Q
from django.db.utils import DEFAULT_DB_ALIAS

from app.financial.models import HighChartMapping, Sale, PostalCodeMapping, StatePopulation


class HighChartMappingService:
    state_mapping = HighChartMapping.objects.tenant_db_for(DEFAULT_DB_ALIAS).filter(county_hc_key__isnull=True)
    county_mapping = HighChartMapping.objects.tenant_db_for(DEFAULT_DB_ALIAS).filter(county_hc_key__isnull=False)

    def map_high_chart_sale(self, sale_data: dict, sale_instance: Sale = None):
        #
        country = sale_data.get('country')
        if sale_instance and country is None:
            country = getattr(sale_instance, 'country')
        #
        state = sale_data.get('state')
        if sale_instance and state is None:
            state = getattr(sale_instance, 'state')
        #
        county = sale_data.get('city')
        if sale_instance and county is None:
            county = getattr(sale_instance, 'city')
        #
        postal_code = sale_data.get('postal_code')
        if sale_instance and postal_code is None:
            postal_code = getattr(sale_instance, 'postal_code')

        state_key, county_key = self.get_hc_keys(country, state, county, postal_code)
        population = self.get_population(country, state)
        sale_data['state_key'] = state_key
        sale_data['county_key'] = county_key
        sale_data['population'] = population
        return sale_data

    def get_hc_keys(self, country: str = '', state: str = '', county: str = '', postal_code: str = ''):
        state_key = None
        county_key = None

        possible_fips = PostalCodeMapping.zip_to_fips(postal_code)
        possible_mapping = HighChartMapping.objects.tenant_db_for(DEFAULT_DB_ALIAS).filter(fips__in=possible_fips)

        country_condition = Q(country__iexact=country) | Q(country_postal_code__iexact=country)
        state_condition = Q(state__iexact=state) | Q(state_postal_code__iexact=state)
        county_condition = Q(county__iexact=county) | Q(county_postal_code__iexact=county) | \
                           Q(county_postal_code__iexact=postal_code)

        # Map state-key and county-key from the only possible mapping getting from zip_code
        if possible_mapping.count() == 1:
            state_key = possible_mapping.first().state_hc_key
            county_key = possible_mapping.first().county_hc_key

        # Map state-key and county-key from possible mapping getting from zip_code
        if possible_mapping.count() > 1:
            res = possible_mapping.filter(country_condition, state_condition, county_condition).first()
            state_key = res.state_hc_key if res else possible_mapping.first().state_hc_key
            county_key = res.county_hc_key if res else possible_mapping.first().county_hc_key

        # Map state-key by sale.state
        if not state_key:
            state_res = self.state_mapping.filter(country_condition, state_condition).first()
            state_key = state_res.state_hc_key if state_res else None

        # Map county-key by sale.state, sale.city
        if not county_key:
            county_res = self.county_mapping.filter(country_condition, state_condition, county_condition).first()
            county_key = county_res.county_hc_key if county_res else None

        return state_key, county_key

    @staticmethod
    def get_population(country: str = '', state: str = ''):
        country_condition = Q(country__iexact=country) | Q(country_postal_code__iexact=country)
        state_condition = Q(state__iexact=state) | Q(state_postal_code__iexact=state)
        try:
            return StatePopulation.objects.tenant_db_for(DEFAULT_DB_ALIAS).get(country_condition, state_condition)
        except StatePopulation.DoesNotExist:
            return None
