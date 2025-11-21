from app.financial.services.postgres_fulltext_search import IFieldConfigPostgresFulltextSearch

config_shipping_items_search = [
    IFieldConfigPostgresFulltextSearch(field_name='sku', weight='A'),
    IFieldConfigPostgresFulltextSearch(field_name='asin', weight='B'),
    IFieldConfigPostgresFulltextSearch(field_name='upc', weight='C'),
    IFieldConfigPostgresFulltextSearch(field_name='fulfillment_type__name', weight='C'),
    IFieldConfigPostgresFulltextSearch(field_name='size__name', weight='C'),
    IFieldConfigPostgresFulltextSearch(field_name='style__name', weight='C'),
    IFieldConfigPostgresFulltextSearch(field_name='title', weight='D'),
    IFieldConfigPostgresFulltextSearch(field_name='description', weight='D'),
]
