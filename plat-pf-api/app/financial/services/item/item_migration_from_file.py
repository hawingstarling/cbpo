import os
from django.db.models import Q
from rest_auth import serializers
from rest_framework.exceptions import ValidationError
from app.core.logger import logger
from app.financial.models import Item, Brand
from app.financial.services.utils.helper import bulk_sync
from app.financial.services.item.read_file_csv import ReadFileCsv
from app.financial.sub_serializers.item_serializer import ItemLargeImportSerializer


class ItemMigration:
    def __init__(self, client_id: str, file_path: str, chunks: int):
        self.__client_id = client_id
        self.__file_path = file_path

        if not os.path.exists('./bucket'):
            os.makedirs('./bucket')

        self.csv_reader = ReadFileCsv(file_path, chunks)

    def handle(self):
        total_success = 0
        total_invalid = 0
        total_error = 0

        brand_bucket = {item.name: item for item in Brand.objects.tenant_db_for(self.__client_id).all()}

        for index, part in enumerate(self.csv_reader.read_parts()):
            logger.info(f'{self.__class__.__name__} part {index + 1}')
            data = []
            invalid_data = set()
            num_success = 0
            num_error = 0
            num_invalid = 0
            for rec in part:
                try:
                    serializer = ItemLargeImportSerializer(data=rec, context={"brand_bucket": brand_bucket,
                                                                              "client_id": self.__client_id})
                    serializer.is_valid(raise_exception=True)
                    validated_data = serializer.validated_data
                    data.append(Item(client_id=self.__client_id,
                                     sku=validated_data['sku'],
                                     asin=validated_data['asin'],
                                     brand=validated_data['brand'],
                                     is_removed=False))
                    num_success += 1
                except serializers.ValidationError or ValidationError:
                    invalid_data.add('{}\n'.format(serializer.initial_data.get('brand', '\n')))  # noqa
                    num_invalid += 1
                    continue
                except Exception as error:
                    logger.error(f'{error}')
                    num_error += 1

            part_validation_stats = {
                'num_success': num_success,
                'num_invalid': num_invalid,
                'num_error': num_error
            }

            total_success += num_success
            total_invalid += num_invalid
            total_error += num_error

            logger.info(f'{self.__class__.__name__} part {index + 1} validation {part_validation_stats}')

            if not len(data):
                continue

            part_import_stats = bulk_sync(
                client_id=self.__client_id,
                new_models=data,
                filters=Q(client_id=self.__client_id),
                key_fields=['client', 'sku'],
                fields=['client', 'sku', 'is_removed', 'asin', 'brand'],
                skip_deletes=True)

            if len(invalid_data):
                missing_data_file = open(f'./bucket/missing_brand_{index + 1}.txt', 'w')
                missing_data_file.writelines(invalid_data)
                missing_data_file.close()

            logger.info(f'{self.__class__.__name__} part {index + 1} import {part_import_stats}')

        total = {
            'total_success': total_success,
            'total_invalid': total_invalid,
            'total_error': total_error
        }
        logger.info(f'{self.__class__.__name__} Total: {total}')
