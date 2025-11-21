from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    page_size_query_param = 'limit'


class OrganizationClientResultsSetPagination(StandardResultsSetPagination):
    page_size = 250
