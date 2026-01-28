CBPO Data Import
---
CBPO Data Import is a Django app to support generate data import file csv, excel. For each question,
visitors can choose between a fixed number of answers.
---

Install requirement
------------
* **Python**: 3.10+
* **Django**: 3.1+
* **DRF**: 3.114+
* **DRF-YASG**: 1.21.5+
* **Openpyxl**: 3.1.2+
* **Pandas**: 2.0.1+
* **Xlsxwriter**: 3.1.9+
* **Maya**: 0.6.1+
* **Google-cloud-storage**: 2.9.0+
* **Django-celery-beat**: 2.5.0

Quick start
------------
```
1. Install package : --extra-index-url http://python-registry.channelprecision.com/simple --trusted-host python-registry.channelprecision.com
django-plat-import-lib-api==<version>

2. Add "plat_import_lib_api" to your INSTALLED_APPS setting:

    INSTALLED_APPS = [
        ...
        'plat_import_lib_api',
    ]
3. add config to settings/common::
    # Recommend using
    FILE_UPLOAD_HANDLERS = [
        'django.core.files.uploadhandler.TemporaryFileUploadHandler',
        'django.core.files.uploadhandler.MemoryFileUploadHandler',
    ]
4. Include the plat_import_lib_api URLconf in your project urls.py like this::

    url(r'^imports/', include('plat_import_lib_api.urls')),

5. Run `python manage.py migrate` to create the DataImportTemporary models.

6. Visit http://127.0.0.1:8000/docs to participate in the plat_import_lib_api.

7. Add & update setting config lib import
    Visit http://127.0.0.1:8000/admin/plat_import_lib_api/setting/
```

Development
------------
```
1. Structure BaseModule
    class BaseModule(object):
        __NAME__ = None
        __MODEL__ = models.Model
        __LABEL__ = None
        __TEMPLATE_VERSION__ = '1.0'
        __TEMPLATE_NUMBER_RECORD__ = 5
        __SERIALIZER_CLASS__ = None
        __PERMISSION_CLASS__ = []  # permissions class setup to api view

        def __init__(self, **kwargs):
            self.kwargs = kwargs
            self.serializer_handle = SerializerHandle(serializer=self.serializer_class,
                                                    regex_pattern_map_config=self.regex_pattern_map_config,
                                                    **self.kwargs)

            self.validate_module()
            #
            self.fields_model_accept = [i.name for i in self.__MODEL__._meta.fields]

        @property
        def permissions_class(self):
            return self.__PERMISSION_CLASS__

        def validate_module(self):
            if not self.__SERIALIZER_CLASS__:
                raise NotImplementedError
            if not self.__PERMISSION_CLASS__:
                raise NotImplementedError

        @property
        def name(self):
            return self.__NAME__

        @property
        def label(self):
            return self.__LABEL__

        @property
        def model(self):
            return self.__MODEL__

        @property
        def data_sample(self):
            """
            using for make sample import file
            Structure:
                {
                    "column_name1" : ["sample_data1", "sample_data11"],
                    "column_name2" : ["sample_data2", "sample_data22", "sample_data222"],
                }
            :return:
            """
            return {}

        @property
        def template(self):
            url, exist = generate_url_sample(self.__NAME__, self.__TEMPLATE_VERSION__)
            if not exist:
                generate_file_sample(
                    self.__NAME__,
                    self.target_cols,
                    self.__TEMPLATE_VERSION__,
                    self.__TEMPLATE_NUMBER_RECORD__,
                    self.data_sample)

            return url

        @property
        def serializer_class(self):
            return self.__SERIALIZER_CLASS__

        @property
        def columns(self) -> list:
            """
            public to api detail
            Structure:
                {
                    name : <name column define serializer>,
                    label : <label column define serializer>,
                    type : <type column define serializer>
                }
            :return:
            """
            return self.serializer_handle.columns

        @property
        def target_cols(self) -> list:
            """
            using for handler background
            Structure:
                {
                    name : <name column define serializer>,
                    label : <label column define serializer>,
                    type : <type column define serializer>,
                    name_detector : <list regex pattern find map to upload column>
                }
            :return:
            """
            return self.serializer_handle.target_cols

        @property
        def regex_pattern_map_config(self):
            """
            document : https://docs.python.org/3.6/howto/regex.html
            Regex pattern for map target column to upload column with list regex pattern config
            structure:
                {
                    '<name_column_define>: [...]
                }
            :return:
            """
            return {}

        def setup_metadata(self, meta, context_serializer, **kwargs) -> dict:
            """
            Method call when make record upload
            :param meta:
            :param context_serializer:
            :param kwargs:
            :return:
            """
            request = context_serializer.get('request')
            params_request = context_serializer.get('view').kwargs
            try:
                for key in params_request.keys():
                    val = params_request[key]
                    if isinstance(val, uuid.UUID):
                        val = str(val)
                    meta.update({key: val})
                user_request = request.user
                if hasattr(user_request, 'user_id'):
                    meta.update({'user_id': str(request.user.user_id)})
                if kwargs:
                    meta.update(kwargs)
            except Exception as ex:
                logger.error(f'[BaseModule][setup_metadata][request] {ex}')
            return meta

        def handler_response_detail(self, response_data, **kwargs) -> dict:
            return response_data

        def validate_request_api_view(self, request, *args, **kwargs):
            raise NotImplementedError

        def upload(self, lib_import_id: str = None, **kwargs) -> any:
            service = LibUploadAction(lib_import_id=lib_import_id, **kwargs)
            service.process()

        def handler_validate_row(self, lib_import_id: str, validated_data: dict, row: dict, map_config: list, errors: dict,
                                data_request: dict, **kwargs):
            pass

        def handler_message_error_column_validate(self, lib_import_id: str, column: str, value: any, errors: list,
                                                **kwargs) -> list:
            return errors

        def validate(self, lib_import_id: str, map_config_request: list, **kwargs) -> any:
            action = LibValidateAction(lib_import_id=lib_import_id, map_config_request=map_config_request, **kwargs)
            action.process()

        def process(self, lib_import_id: str, **kwargs) -> any:
            action = LibProcessAction(lib_import_id=lib_import_id, **kwargs)
            action.process()

        def export(self, lib_import_id: str, filters: dict = {}, **kwargs):
            export = ExportService(lib_import_id=lib_import_id, filters=filters)
            return export.process()

        def handler_validated_data(self, lib_import_id: str, validated_data: dict, **kwargs):
            """
            Handler validated data step process for make instance
            """
            return validated_data

        def keys_raw_map_config(self, lib_import_id: str, validated_data, **kwargs):
            return {
                'key_map': [],
                'parent_key_map': [],
            }

        def filter_instance(self, lib_import_id: str, validated_data, **kwargs):
            """
            define filter instance for update case step process
            Structure :
                {
                    column : validation_date[<name>]
                }
            """
            raise NotImplementedError

        @property
        def model_objects(self):
            if hasattr(self.model, 'all_objects'):
                model_objects = self.model.all_objects
            else:
                model_objects = self.model.objects
            return model_objects

        def find_instance(self, lib_import_id: str, validated_data: dict, **kwargs):
            try:
                filters = self.filter_instance(lib_import_id, validated_data, **kwargs)
                return self.model_objects.get(**filters)
            except Exception as ex:
                logger.error(ex)
                return None

        def make_instance(self, lib_import_id: str, validated_data: dict, **kwargs):
            instance = self.find_instance(lib_import_id, validated_data, **kwargs)
            created = True
            #
            validated_data_copy = copy.deepcopy(validated_data)
            fields_diff = list(set(validated_data_copy.keys()) - set(self.fields_model_accept))
            for key in fields_diff:
                try:
                    del validated_data_copy[key]
                except Exception as ex:
                    pass
            #
            if instance:
                obj = copy.deepcopy(instance)
                for key, item in validated_data_copy.items():
                    setattr(obj, key, item)
                if hasattr(self.model, 'is_removed') and hasattr(self.model, 'all_objects'):
                    setattr(obj, 'is_removed', False)
                if hasattr(self.model, 'modified'):
                    setattr(obj, 'modified', timezone.now())
                created = False
            else:
                obj = self.model(**validated_data_copy)
            return obj, created

        def handler_bulk_process(self, lib_import_id: str, bulk_insert: list, bulk_update: list, **kwargs):
            pass

        @property
        def field_model_accept_update(self):
            return [i.name for i in self.model._meta.fields if i.name not in ['pk', 'id']]

        def bulk_process(self, lib_import_id: str, bulk_insert: list, bulk_update: list, **kwargs):
            """
            process insert or update data per chunk list data step process
            """
            # handler pre bulk process
            self.handler_bulk_process(lib_import_id, bulk_insert, bulk_update, **kwargs)

            self.model_objects.bulk_create(bulk_insert, ignore_conflicts=True)
            self.model_objects.bulk_update(bulk_update, fields=self.field_model_accept_update)

2. Module sample
    from plat_import_lib_api.services.modules.base import BaseModule
    class AsinTest(BaseModule):
        __NAME__ = "AsinTest"
        __MODEL__ = AsinTestModel
        __LABEL__ = "Asin Test"
        __SERIALIZER_CLASS__ = AsinTestSerializer
        __PERMISSION_CLASS__ = [AllowAny]

        def setup_metadata(self, context_serializer):
            """
            - Handler add meta to record import lib step upload
            - Default add kwargs request to meta
            """
            meta = super().setup_metadata(context_serializer)
            // your custom meta
            return meta

        def handler_validated_data(self, import_temp_id: str, validated_data: dict, **kwargs):
            meta = self.model_objects.get(pk=import_temp_id).meta
            validated_data['client'] = ClientPortal.objects.get(pk=meta['client_id'])
            return validated_data
        
        def filter_instance(self, validated_data, **kwargs):
            return {
                        'brand': validated_data.get('brand'),
                        'sku': validated_data.get('sku')
                    }
        
        @property
        def regex_pattern_map_config(self):
            # your define
            # this is sample
            return {
                'profile_id': ['profile id', f'(profile|pro id)'],
                'brand': [f'(brand|brand name)', 'brand'],
                'channel': [r'^channel$', r'channel name']
            }

        def validate_request_api_view(self, request, *args, **kwargs):
            # your custom
            # this is sample
            try:
                client_id = kwargs['client_id']
                ClientPortal.objects.get(pk=meta['client_id'])
            except Exception as ex:
                raise InvalidParamException(msg=ex, verbose=true)

        def handler_message_error_column_validate(self, lib_import_id: str, column: str, value: any, errors: list,
                                                  **kwargs):
            # your custom
            # this is sample
            msg = {
                    "key": column,
                    "message": f"{value} must lowercase"
                }
            errors.append(msg)
            return errors
        
        def handler_bulk_process(self, lib_import_id: str, bulk_insert: list, bulk_update: list, **kwargs):
            # your custom
            # this is sample case
            data = []

            total_items = bulk_insert + bulk_update       
            for item in bulk_update:
                origin = None
                try:
                    origin = self.model_objects.get(pk=item.pk)
                except self.model.DoesNotExist:
                    pass
                log_instance = LogEntryService.make_log(origin=origin, update=item)
                if log is not None:
                   data.append(log_instance)
            LogEntry.objects.bulk_create(data)
    
```

Upgrade
------------
```
 Please contact with Admin IT
```

Build dist & test
------------
```
1. $ python setup.py sdist
2. Find folder dist -> file zip
3. Copy to source project
4. $ pip install <file zip>
```

Uninstall
------------
```
$ pip uninstall django-plat-import-lib-api
```

UnitTest
------------
```
$ python manage.py test plat_import_lib_api
```