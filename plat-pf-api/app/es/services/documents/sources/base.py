import math
import uuid
import logging
from abc import ABC
from time import sleep
from typing import Union, List, Dict
from django.db import connections
from elasticsearch import Elasticsearch, helpers
from elasticsearch.exceptions import RequestError

from app.core.utils import has_valid_value
from app.es.helper import get_es_host_client, get_es_settings_client
from app.es.variables.config import ES_TIMEOUT, ACTIONS_TYPE, ES_BULK_SIZE, ES_UPDATE_ACTION, \
    ES_UPSERT_ACTION, ES_DELETE_ACTION, ES_MAX_RETRY, ES_TIME_SLEEP
from app.database.helper import get_connection_workspace
from ..abstract import SourceDocumentAbstract
from rest_framework import status

logger = logging.getLogger(__name__)


class DataSourceDocumentBase(SourceDocumentAbstract, ABC):
    INDEX_TEMPLATE = None

    def __init__(self, client_id: str, *args, **kwargs):
        self.client_id = client_id
        self.host = get_es_host_client(self.client_id)
        self.settings = get_es_settings_client(self.client_id)
        self.db_using = get_connection_workspace(self.client_id)
        self.es = Elasticsearch(hosts=[self.host], timeout=ES_TIMEOUT)
        self.args = args
        self.kwargs = kwargs
        self.properties_settings = self.kwargs.get('properties_settings', {})
        self.retry = 0
        self.success = 0
        self.failed_ids = []

    @property
    def index(self):
        return self.INDEX_TEMPLATE.format(client_id=self.client_id.replace('-', '_'))

    @property
    def column_id(self):
        return

    @property
    def get_index_body(self):
        return {
            "settings": self.settings
        }

    @property
    def es_bulk_size(self):
        return self.kwargs.get('es_bulk_size', ES_BULK_SIZE)

    @property
    def type_flatten(self):
        return self.kwargs.get('type_flatten', None)

    @property
    def exist_index(self):
        return self.es.indices.exists(index=self.index)

    def set_mappings_properties(self, attrs: dict):
        try:
            assert attrs is not None, "Attrs is not empty"
            properties = self.settings.get(
                "mappings", {}).get("properties", {})
            for key in attrs.keys():
                if key not in properties:
                    properties.update({key: attrs[key]})
            self.settings["mappings"].update(dict(properties=properties))
        except Exception as ex:
            logger.error(
                f"[{self.__class__.__name__}][{self.index}][set_mappings_properties] {ex}")

    def search(self, query: Dict):
        if not self.exist_index:
            logger.info(
                f"[{self.__class__.__name__}][{self.index}][search] Index already dropped")
            return
        logger.info(
            f"[{self.__class__.__name__}][{self.index}][search] Beginning ...")
        try:
            logger.debug(
                f"[{self.__class__.__name__}][{self.index}][query] Query: {query}")
            response = self.es.search(index=self.index, body=query)
            logger.debug(
                f"[{self.__class__.__name__}][{self.index}][search] Response: {response}")
            return response
        except Exception as ex:
            logger.error(
                f"[{self.__class__.__name__}][{self.index}][search] {ex}")
            raise ex

    def sync_settings_index(self):
        if not self.exist_index:
            return self.create_index()

        logger.info(
            f"[{self.__class__.__name__}][{self.index}][sync_settings_index] Beginning ...")
        try:
            # Get Properties Settings Config
            __properties_settings_config = self.settings["settings"]
            logger.debug(
                f"[{self.__class__.__name__}][{self.index}][sync_settings_index] "
                f"Properties Settings Config: {__properties_settings_config}"
            )

            # Get Properties Settings Index
            try:
                __properties_settings_index = self.es.indices.get_settings(index=self.index)[
                    self.index]["settings"]
            except Exception as ex:
                logger.error(
                    f"[{self.__class__.__name__}][{self.index}][sync_settings_index] {ex}")
                __properties_settings_index = {}
            logger.debug(
                f"[{self.__class__.__name__}][{self.index}][sync_settings_index] "
                f"Properties Settings Index: {__properties_settings_index}"
            )

            __properties_settings_update: Dict = {}
            # Get Properties Settings Update
            if not __properties_settings_index:
                __properties_settings_update = __properties_settings_config
            else:
                for key, vals in __properties_settings_config.items():
                    try:
                        __data: Dict = {}
                        __val_key_settings: Dict = __properties_settings_index.get(key) if key == "index" \
                            else __properties_settings_index["index"].get(key)
                        for _key, _val in vals.items():
                            __val_settings_index = __val_key_settings.get(_key)
                            logger.debug(
                                f"[{self.__class__.__name__}][{self.index}][sync_settings_index] "
                                f"Key={key} , Attr={_key}, Value={_val}, Setting Index={__val_settings_index}"
                            )
                            if _val != __val_settings_index:
                                __data.update({_key: _val})
                        if __data:
                            __properties_settings_update.update({key: __data})
                    except Exception as ex:
                        logger.error(
                            f"[{self.__class__.__name__}][{self.index}][sync_settings_index][key={key}] {ex}")

            if not __properties_settings_update:
                logger.info(
                    f"[{self.__class__.__name__}][{self.index}][sync_settings_index] Not found properties for sync"
                )
                return

            logger.info(
                f"[{self.__class__.__name__}][{self.index}][sync_settings_index] "
                f"Body: {__properties_settings_update}"
            )
            # Close the index
            self.es.indices.close(index=self.index)
            # Update settings
            response = self.es.indices.put_settings(
                index=self.index, body=self.settings["settings"])
            logger.info(
                f"[{self.__class__.__name__}][{self.index}][sync_settings_index] Response: {response}")
            # Reopen the index
            self.es.indices.open(index=self.index)
        except Exception as ex:
            logger.error(
                f"[{self.__class__.__name__}][{self.index}][sync_settings_index] {ex}")
            raise ex

    def sync_mappings_index(self):
        assert len(list(self.properties_settings.keys())
                   ) > 0, "Attrs is not empty"
        self.set_mappings_properties(self.properties_settings)

        __properties_mapping_update = {}

        # Get Properties Mappings Config
        __properties_mappings_config = self.settings["mappings"]["properties"]
        logger.debug(
            f"[{self.__class__.__name__}][{self.index}][sync_mappings_index] "
            f"Properties Mappings Config: {__properties_mappings_config}"
        )

        # Get Properties Mappings Index
        try:
            __properties_mappings_index = list(
                self.es.indices.get_mapping(index=self.index)[self.index]["mappings"]["properties"].keys())
        except Exception as ex:
            logger.error(
                f"[{self.__class__.__name__}][{self.index}][sync_mappings_index] {ex}")
            __properties_mappings_index = {}
        logger.debug(
            f"[{self.__class__.__name__}][{self.index}][sync_mappings_index] "
            f"Properties Mappings Index: {__properties_mappings_index}"
        )

        # Get Properties Mappings Update
        if not __properties_mappings_index:
            __properties_mapping_update = __properties_mappings_config
        else:
            for key, val in __properties_mappings_config.items():
                if key not in __properties_mappings_index:
                    __properties_mapping_update.update({key: val})

        if not __properties_mapping_update:
            logger.info(
                f"[{self.__class__.__name__}][{self.index}][sync_mappings_index] Not found properties for sync"
            )
            return

        logger.info(
            f"[{self.__class__.__name__}][{self.index}][sync_mappings_index] "
            f"Properties Mappings Update: {__properties_mapping_update}"
        )
        body = {"properties": __properties_mapping_update}
        logger.info(
            f"[{self.__class__.__name__}][{self.index}][sync_mappings_index] Body: {body}")
        response = self.es.indices.put_mapping(
            body=body, index=self.index, ignore=[400, 404])
        logger.info(
            f"[{self.__class__.__name__}][{self.index}][sync_mappings_index] Response: {response}")

    def drop_index(self):
        if not self.exist_index:
            logger.info(
                f"[{self.__class__.__name__}][{self.index}][drop_index] Index already dropped")
            return
        logger.info(
            f"[{self.__class__.__name__}][{self.index}][drop_index] Beginning ...")
        try:
            response = self.es.indices.delete(
                index=self.index, ignore=[400, 404])
            logger.info(
                f"[{self.__class__.__name__}][{self.index}][drop_index] {response}")
        except Exception as ex:
            logger.error(
                f"[{self.__class__.__name__}][{self.index}][drop_index] {ex}")
            raise ex

    def create_index(self):
        if self.exist_index:
            logger.info(
                f"[{self.__class__.__name__}][{self.index}][create_index] Index already exists")
            return False

        logger.info(
            f"[{self.__class__.__name__}][{self.index}][create_index] Beginning ...")

        try:
            logger.debug(
                f"[{self.__class__.__name__}][{self.index}][create_index] Body: {self.settings}")

            response = self.es.indices.create(
                index=self.index,
                body=self.settings,
                timeout="30s"  # Add timeout
            )

            logger.info(
                f"[{self.__class__.__name__}][create_index] Index created successfully, Response: {response}"
            )

            if self.properties_settings:
                self.sync_mappings_index()

            return True

        except RequestError as ex:
            # Handle the common case where index is created by another process
            if 'resource_already_exists_exception' in str(ex):
                logger.info(
                    f"[{self.__class__.__name__}][{self.index}][create_index] Index created by another process")
                return False
            else:
                logger.error(
                    f"[{self.__class__.__name__}][{self.index}][create_index] Elasticsearch error: {ex}")
                raise

        except Exception as ex:
            logger.error(
                f"[{self.__class__.__name__}][{self.index}][create_index] {ex}")
            raise

    def delete_all_docs(self):
        if not self.exist_index:
            logger.info(
                f"[{self.__class__.__name__}][{self.index}][delete_all_docs] Index not exist")
            return
        logger.info(
            f"[{self.__class__.__name__}][{self.index}][delete_all_docs] Beginning ...")
        try:
            # Delete all documents but keep the index
            query = {
                "query":
                    {
                        "match_all": {}
                    }
            }
            logger.debug(
                f"[{self.__class__.__name__}][{self.index}][delete_all_docs] Body: {query}")
            response = self.es.delete_by_query(index=self.index, body=query)
            logger.info(
                f"[{self.__class__.__name__}][delete_all_docs] Response: {response}")
        except Exception as ex:
            logger.error(
                f"[{self.__class__.__name__}][{self.index}][delete_all_docs] {ex}")
            raise ex

    def delete_old_docs(self, time_threshold: str, batch_size: int = 1000, max_retries: int = 3):
        """
        Delete old documents from Elasticsearch index with proper conflict handling.

        Args:
            time_threshold: Time threshold for deletion (e.g., "now-30d")
            batch_size: Number of documents to process in each batch
            max_retries: Maximum number of retries for failed operations
        """
        if not self.exist_index:
            logger.info(
                f"[{self.__class__.__name__}][{self.index}][delete_old_docs] Index not exist")
            return

        logger.info(
            f"[{self.__class__.__name__}][{self.index}][delete_old_docs] Beginning ...")

        # First, check how many documents will be affected
        count_query = {
            "query": {
                "range": {
                    "modified": {
                        "lt": time_threshold
                    }
                }
            }
        }

        try:
            # Get count of documents to be deleted
            count_response = self.es.count(index=self.index, body=count_query)
            total_docs = count_response['count']
            logger.info(
                f"[{self.__class__.__name__}][{self.index}][delete_old_docs] Found {total_docs} documents to delete")

            if total_docs == 0:
                logger.info(
                    f"[{self.__class__.__name__}][{self.index}][delete_old_docs] No documents to delete")
                return {'deleted': 0, 'version_conflicts': 0}

            # Prepare delete query
            delete_query = {
                "query": {
                    "range": {
                        "modified": {
                            "lt": time_threshold
                        }
                    }
                }
            }

            logger.debug(
                f"[{self.__class__.__name__}][{self.index}][delete_old_docs] Body: {delete_query}")

            # Execute delete with conflict handling
            response = self.es.delete_by_query(
                index=self.index,
                body=delete_query,
                conflicts="proceed",  # Continue despite version conflicts
                refresh=True,  # Refresh index after deletion
                wait_for_completion=True,  # Wait for completion
                request_timeout=300,  # 5 minute timeout
                scroll_size=batch_size,  # Process in batches
                max_docs=total_docs  # Limit to expected number of docs
            )

            # Log detailed results
            deleted_count = response.get('deleted', 0)
            conflict_count = response.get('version_conflicts', 0)
            total_processed = response.get('total', 0)
            took_time = response.get('took', 0)

            logger.info(
                f"[{self.__class__.__name__}][{self.index}][delete_old_docs] "
                f"Completed in {took_time}ms. "
                f"Total: {total_processed}, Deleted: {deleted_count}, "
                f"Conflicts: {conflict_count}"
            )

            # Handle conflicts if any
            if conflict_count > 0:
                logger.warning(
                    f"[{self.__class__.__name__}][{self.index}][delete_old_docs] "
                    f"{conflict_count} documents had version conflicts and were not deleted. "
                    f"This is normal and indicates concurrent modifications."
                )

                # Optionally retry conflicts (if needed)
                if conflict_count > 0 and max_retries > 0:
                    logger.info(
                        f"[{self.__class__.__name__}][{self.index}][delete_old_docs] Retrying conflicts...")
                    return self._retry_delete_conflicts(delete_query, max_retries)

            return {
                'deleted': deleted_count,
                'version_conflicts': conflict_count,
                'total_processed': total_processed,
                'took_ms': took_time
            }

        except Exception as ex:
            logger.error(
                f"[{self.__class__.__name__}][{self.index}][delete_old_docs] {ex}")

            # If it's a ConflictError, provide more specific logging
            if "ConflictError" in str(type(ex)):
                logger.warning(
                    f"[{self.__class__.__name__}][{self.index}][delete_old_docs] "
                    f"Version conflicts occurred. Some documents were not deleted due to concurrent modifications."
                )
                # You might want to return partial success here instead of raising
                # return {'error': 'conflicts', 'message': str(ex)}

            raise ex

    def _retry_delete_conflicts(self, original_query: dict, max_retries: int = 3) -> dict:
        """
        Retry delete operation for documents that had version conflicts.

        Args:
            original_query: The original delete query
            max_retries: Maximum number of retry attempts

        Returns:
            Dictionary with retry results
        """
        retry_count = 0
        total_deleted = 0
        total_conflicts = 0

        while retry_count < max_retries:
            try:
                # Small delay before retry
                import time
                time.sleep(0.5 * (retry_count + 1))  # Exponential backoff

                response = self.es.delete_by_query(
                    index=self.index,
                    body=original_query,
                    conflicts="proceed",
                    refresh=True,
                    request_timeout=60,
                    scroll_size=100  # Smaller batch for retries
                )

                deleted = response.get('deleted', 0)
                conflicts = response.get('version_conflicts', 0)

                total_deleted += deleted
                total_conflicts += conflicts

                logger.info(
                    f"[{self.__class__.__name__}][{self.index}][retry_delete_conflicts] "
                    f"Retry {retry_count + 1}: Deleted {deleted}, Conflicts {conflicts}"
                )

                # If no more conflicts, we're done
                if conflicts == 0:
                    break

                retry_count += 1

            except Exception as ex:
                logger.error(
                    f"[{self.__class__.__name__}][{self.index}][retry_delete_conflicts] "
                    f"Retry {retry_count + 1} failed: {ex}"
                )
                retry_count += 1

        return {
            'retry_deleted': total_deleted,
            'retry_conflicts': total_conflicts,
            'retry_attempts': retry_count
        }

    # Alternative: Simpler version if you just want to ignore conflicts
    def delete_old_docs_simple(self, time_threshold: str):
        """
        Simplified version that just ignores version conflicts.
        """
        if not self.exist_index:
            logger.info(
                f"[{self.__class__.__name__}][{self.index}][delete_old_docs] Index not exist")
            return

        logger.info(
            f"[{self.__class__.__name__}][{self.index}][delete_old_docs] Beginning ...")

        try:
            query = {
                "query": {
                    "range": {
                        "modified": {
                            "lt": time_threshold
                        }
                    }
                }
            }

            logger.debug(
                f"[{self.__class__.__name__}][{self.index}][delete_old_docs] Body: {query}")

            # Simply add conflicts="proceed" to ignore version conflicts
            response = self.es.delete_by_query(
                index=self.index,
                body=query,
                conflicts="proceed"  # This is the key addition
            )

            # Log success with conflict information
            deleted = response.get('deleted', 0)
            conflicts = response.get('version_conflicts', 0)

            if conflicts > 0:
                logger.info(
                    f"[{self.__class__.__name__}][{self.index}][delete_old_docs] "
                    f"Completed: {deleted} deleted, {conflicts} conflicts (ignored)"
                )
            else:
                logger.info(
                    f"[{self.__class__.__name__}][{self.index}][delete_old_docs] "
                    f"Completed: {deleted} deleted, no conflicts"
                )

            return response

        except Exception as ex:
            logger.error(
                f"[{self.__class__.__name__}][{self.index}][delete_old_docs] {ex}")
            raise ex

    def on_validate(self):
        logger.info(
            f"[{self.__class__.__name__}][{self.index}][on_validate] Beginning ...")
        assert self.INDEX_TEMPLATE is not None, "Index template not define"

    def _create_docs_actions(self, data: Union[str, List[Dict]], action: str, key_id: str):
        assert action in ACTIONS_TYPE, f"{action} must value in {ACTIONS_TYPE}"
        logger.info(
            f"[{self.__class__.__name__}][{self.index}][_create_docs_action] Beginning ...")
        try:
            doc_as_upsert = (action == ES_UPSERT_ACTION)

            def generate_doc(doc):
                """Generates a document based on the provided action."""
                _id = doc.get(key_id, uuid.uuid4())
                logger.debug(
                    f"[{self.__class__.__name__}][{self.index}][_create_docs_actions] Docs = {doc}")

                base_doc = {"_index": self.index,
                            "_op_type": action, "_id": _id}
                if action in [ES_UPDATE_ACTION, ES_UPSERT_ACTION]:
                    base_doc.update(
                        {"doc": doc, "_op_type": ES_UPDATE_ACTION, "doc_as_upsert": doc_as_upsert})
                elif action not in [ES_DELETE_ACTION]:
                    base_doc["doc"] = doc

                return base_doc

            if isinstance(data, str):
                with connections[self.db_using].cursor() as cursor:
                    cursor.execute(data)
                    columns = [col[0] for col in cursor.description]
                    for row in cursor.fetchall():
                        yield generate_doc(dict(zip(columns, row)))
            elif isinstance(data, list):
                for item in data:
                    yield generate_doc(item)
        except Exception as ex:
            logger.error(
                f"[{self.__class__.__name__}][{self.index}][_create_docs_action] {ex}")
            raise ex

    def on_process(self, data: Union[str, List[Dict]], action: str, key_id: str):
        logger.info(
            f"[{self.__class__.__name__}][{self.index}][on_process] Beginning ...")
        try:
            assert has_valid_value(data) is True, f"Data has invalid value"
            self.success = 0
            self.failed_ids = []
            # count record
            total_records = self.get_total_records_data(data)
            if total_records == 0:
                logger.info(
                    f"[{self.__class__.__name__}][{self.index}][on_process] Not found records")
                return self.success, self.failed_ids
            logger.info(
                f"[{self.__class__.__name__}][{self.index}][on_process] Total records = {total_records}")
            self._on_process_bulk_size_standard(
                total_records, data, action, key_id)
            return self.success, self.failed_ids
        except Exception as ex:
            logger.error(
                f"[{self.__class__.__name__}][{self.index}][on_process] {ex}")
            raise ex

    def get_total_records_data(self, data: Union[str, List[Dict]]) -> int:
        """
        Returns the total number of records in the given data.

        :param data: SQL query string or list of dictionaries.
        :return: Total number of records.
        :raises NotImplementedError: If data type is unsupported.
        """
        if isinstance(data, list):
            return len(data)

        if isinstance(data, str):
            return self._get_total_records_from_query(data)

        raise NotImplementedError(f"Unsupported data type: {type(data)}")

    def _get_total_records_from_query(self, query: str) -> int:
        """
        Executes a SQL COUNT query to get the total number of records.

        :param query: SQL query string.
        :return: Count of records.
        """
        try:
            # Ensure no trailing semicolon
            sanitized_query = query.replace(";", "")
            sql_count = f"SELECT COUNT(*) FROM ({sanitized_query}) AS table_count;"

            with connections[self.db_using].cursor() as cursor:
                cursor.execute(sql_count)
                res = cursor.fetchone()
                return res[0] if res else 0  # Return 0 if no result found

        except Exception as ex:
            logger.error(
                f"[{self.__class__.__name__}][{self.index}][get_total_records_data] {ex}")
            return 0  # Returning 0 instead of raising an exception to avoid breaking flow

    def _on_process_bulk_size_standard(self, total_records: int, data: Union[str, List[Dict]], action: str,
                                       key_id: str):
        """
        Handles bulk processing when data size exceeds Elasticsearch bulk limit.

        :param total_records: Total number of records.
        :param data: SQL query string or list of data.
        :param action: Elasticsearch action type.
        :param key_id: Unique identifier for each document.
        """
        total_pages = math.ceil(total_records / self.es_bulk_size)
        logger.info(
            f"[{self.__class__.__name__}][{self.index}][_on_process_bulk_size_standard] Total pages = {total_pages}")

        if total_pages == 1:
            self._on_run_helpers_bulk(data, action, key_id)
            return

        data_offset = data if isinstance(data, list) else data.replace(
            ";", "")  # Remove semicolon if SQL query

        for page in range(1, total_pages + 1):
            _data_offset = self._get_paginated_data(data_offset, page)
            self._on_run_helpers_bulk(
                _data_offset, action, key_id, "_on_process_bulk_size_standard", page)

    def _get_paginated_data(self, data: Union[str, List[Dict]], page: int) -> Union[str, List[Dict]]:
        """
        Returns paginated data based on the current page and bulk size.

        :param data: SQL query string or list of data.
        :param page: Current page number.
        :return: Modified SQL query with LIMIT and OFFSET or a subset of the list.
        """
        offset = (page - 1) * self.es_bulk_size

        if isinstance(data, str):
            return f"{data} LIMIT {self.es_bulk_size} OFFSET {offset};"

        if isinstance(data, list):
            return data[offset: offset + self.es_bulk_size]

        return data  # Fallback, should never hit

    def _on_run_helpers_bulk(self, data: Union[str, List[Dict]], action, key_id,
                             request_action: str = "_on_process_bulk_size_standard", page: any = None):
        kwargs_info = [self.__class__.__name__, self.index, request_action]
        if page:
            kwargs_info.append(f"Page {page}")
        kwargs_optional = dict(raise_on_error=False)
        # if action == ES_DELETE_ACTION:
        #     kwargs_optional.update(dict(ignore_status=[404]))
        try:
            logger.info(f"[{']['.join(kwargs_info)}] Start bulk ... ")
            # actions = list(self._create_docs_actions(data, action, key_id))
            # logger.info(f"[{']['.join(kwargs_info)}] {actions}")
            # Track errors using stats_only=False
            success, failed_items = helpers.bulk(self.es, self._create_docs_actions(data, action, key_id),
                                                 **kwargs_optional)
            self.success += success
            # Log failed documents
            if failed_items:
                failed_docs = []
                for item in failed_items:
                    # index, create, update, or delete
                    op_type = list(item.keys())[0]
                    failed_doc = item[op_type]
                    failed_docs.append({
                        'id': failed_doc['_id'],
                        'error': failed_doc.get('error', 'result'),
                        'status': failed_doc['status']
                    })
                    if failed_doc['status'] not in [status.HTTP_404_NOT_FOUND]:
                        self.failed_ids.append(failed_doc['_id'])
                logger.error(
                    f"[{']['.join(kwargs_info)}] Failed documents: {failed_docs}")
            logger.info(
                f"[{']['.join(kwargs_info)}] Successful operations: {success}, Failed operations: {len(failed_items)}"
            )
        except Exception as ex:
            logger.error(f"[{']['.join(kwargs_info)}] {ex}")
            if self.retry < ES_MAX_RETRY:
                sleep(ES_TIME_SLEEP)
                self.retry += 1
                logger.info(
                    f"[{self.__class__.__name__}][{self.index}][on_process] Retry {self.retry} time")
                self._on_run_helpers_bulk(
                    data, action, key_id, request_action=request_action, page=page)
            self.retry = 0
            raise ex

    def on_complete(self):
        logger.info(
            f"[{self.__class__.__name__}][{self.index}][on_complete] Done")
