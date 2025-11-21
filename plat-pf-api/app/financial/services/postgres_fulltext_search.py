from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db import models
from django.db.models import Q


class ISortConfigPostgresFulltextSearch:

    def __init__(self, field_name: str, direction: str):
        self.field_name = field_name
        assert direction in ["desc", "asc"], 'direction must be desc or acs'
        self.direction = direction

    @property
    def output_str_sorting(self):
        return f'-{self.field_name}' if self.direction == 'desc' else f'{self.field_name}'


class IFieldConfigPostgresFulltextSearch:

    def __init__(self, field_name: str, weight: str):
        self.field_name = field_name
        assert weight in ['A', 'B', 'C', 'D'], 'weight are A, B, C, D'
        self.weight = weight


class PostgresFulltextSearch:
    model_objects_manager: models.Manager = None
    fields_config: [] = None

    def __init__(self, model_objects_manager: models.Manager,
                 fields_config: [IFieldConfigPostgresFulltextSearch],
                 sort_config: [ISortConfigPostgresFulltextSearch], is_sort=True):
        self.model_objects_manager = model_objects_manager

        if not fields_config:
            self.fields_config = [
                IFieldConfigPostgresFulltextSearch(field_name='additional_data', weight='A'),
                IFieldConfigPostgresFulltextSearch(field_name='changes', weight='B'),
            ]
        else:
            self.fields_config = fields_config

        self.is_sort = is_sort

        self.sort_config = []

        if self.is_sort:
            sort_rank_default = ISortConfigPostgresFulltextSearch(field_name='rank', direction='desc')
            if not sort_config:
                self.sort_config = [sort_rank_default]
            else:
                self.sort_config = [sort_rank_default, *sort_config]

    def search(self, keyword):
        first_config = self.fields_config[0]
        combined_search_vector = SearchVector(first_config.field_name, weight=first_config.weight)
        for index, field_config in enumerate(self.fields_config):
            if index == 0:
                continue
            combined_search_vector += SearchVector(field_config.field_name, weight=field_config.weight)

        search_query = SearchQuery(keyword)

        # search
        res = self.model_objects_manager \
            .annotate(search=combined_search_vector) \
            .filter(search=search_query)
        # rank based search result
        order_by = [item.output_str_sorting for item in self.sort_config]
        res = res.annotate(rank=SearchRank(combined_search_vector, search_query))
        if order_by:
            res = res.order_by(*order_by)
        return res

    def search_rank_on_contain(self, keyword: str):
        """
        fulltext search based on SearchQuery and SearchVector and ranking on it
        :param keyword:
        :return:
        """
        first_config = self.fields_config[0]
        combined_search_vector = SearchVector(first_config.field_name, weight=first_config.weight)
        cond = Q()

        for index, field_config in enumerate(self.fields_config):
            cond.add(Q(**{f"{field_config.field_name}__icontains": keyword}), Q.OR)
            if index == 0:
                continue
            combined_search_vector += SearchVector(field_config.field_name, weight=field_config.weight)

        search_query = SearchQuery(keyword)
        order_by = [item.output_str_sorting for item in self.sort_config]
        return self.model_objects_manager.filter(cond).annotate(
            rank=SearchRank(combined_search_vector, search_query)
        ).order_by(*order_by)
