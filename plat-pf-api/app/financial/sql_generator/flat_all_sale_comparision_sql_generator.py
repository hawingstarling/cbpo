from abc import ABC
from typing import Dict
from app.financial.services.utils.helper import get_analysis_es_service
from app.financial.sql_generator.flat_base_comparison_sql_generator import FlatBaseComparisonSQLGenerator
from app.financial.variable.sale_status_static_variable import SALE_SHIPPED_STATUS


class FlatAllSaleComparisonSQLGenerator(FlatBaseComparisonSQLGenerator, ABC):

    @property
    def config_statement_source(self):
        return {
            # {source column : alias name column}
            # ----------------------------------------------------------------
            "_source_table_.product": {
                "name": "product",
                "pg": {
                    "type": "varchar(255) not null"
                },
                "es": {
                    "type": "text"
                }
            },
            "_source_table_.product_type": {
                "name": "product_type",
                "pg": {
                    "type": "varchar(255) not null"
                },
                "es": {
                    "type": "text"
                }
            },
            "_source_table_.parent_asin": {
                "name": "parent_asin",
                "pg": {
                    "type": "varchar(255) not null"
                },
                "es": {
                    "type": "text"
                }
            },
            "_source_table_.product_description": {
                "name": "product_description",
                "pg": {
                    "type": "varchar(255) not null"
                },
                "es": {
                    "type": "text"
                }
            },
            # -------------------------------------------------
            "_source_table_.d0_unit": {
                "name": "d0_unit",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.d1_unit": {
                "name": "d1_unit",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.d0_amount": {
                "name": "d0_amount",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.d1_amount": {
                "name": "d1_amount",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.d_diff_unit": {
                "name": "d_diff_unit",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.d_diff_amount": {
                "name": "d_diff_amount",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            # -------------------------------------------------
            "_source_table_.y0_30d_unit": {
                "name": "y0_30d_unit",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.y1_30d_unit": {
                "name": "y1_30d_unit",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.y0_30d_amount": {
                "name": "y0_30d_amount",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.y1_30d_amount": {
                "name": "y1_30d_amount",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.y_30d_diff_unit": {
                "name": "y_30d_diff_unit",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.y_30d_diff_amount": {
                "name": "y_30d_diff_amount",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            # -------------------------------------------------
            "_source_table_.y0_ytd_unit": {
                "name": "y0_ytd_unit",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.y1_ytd_unit": {
                "name": "y1_ytd_unit",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.y0_ytd_amount": {
                "name": "y0_ytd_amount",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.y1_ytd_amount": {
                "name": "y1_ytd_amount",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.y_ytd_diff_unit": {
                "name": "y_ytd_diff_unit",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            "_source_table_.y_ytd_diff_amount": {
                "name": "y_ytd_diff_amount",
                "pg": {
                    "type": "numeric"
                },
                "es": {
                    "type": "float"
                }
            },
            # -------------------------------------------------
            "_source_table_.modified": {
                "name": "modified",
                "pg": {
                    "type": "timestamp with time zone not null"
                },
                "es": {
                    "type": "date"
                }
            }
        }

    @property
    def group_by_fields_mappings(self) -> Dict:
        mappings = {
            "product": "product_number",
            "product_type": "product_type",
            "parent_asin": "parent_asin",
            "product_description": "title",
        }
        return mappings

    def build_count_aggregations_unique_combinations(self, client_id, modified_filter: str = None, **kwargs):
        analysis_es_service = get_analysis_es_service(client_id)
        last_year = self.yesterday.year - 1
        fd_last_year = self.yesterday.strftime(f"{last_year}-01-01 00:00:00")
        td_last_year = self.yesterday.strftime(f"{last_year}-%m-%d 23:59:59")
        fd_current_year = self.yesterday.strftime("%Y-01-01 00:00:00")
        td_current_year = self.yesterday.strftime("%Y-%m-%d 23:59:59")

        filter_cond = {
            "bool": {
                "must": [
                    {"term": {"channel_name.keyword": self.ds_channel_default}},
                    {"terms": {"item_sale_status.keyword": [
                        SALE_SHIPPED_STATUS]}},
                    {"exists": {"field": "parent_asin"}},
                    {"exists": {"field": "product_number"}},
                    {
                        "script": {
                            "script": """
                                  doc['parent_asin.keyword'].size() > 0 && doc['parent_asin.keyword'].value != '' &&
                                  doc['product_number.keyword'].size() > 0 && doc['product_number.keyword'].value != ''
                                """
                        }
                    },
                    {
                        "bool": {
                            "should": [
                                {
                                    "range": {
                                        "sale_date": {
                                            "gte": fd_last_year,
                                            "lte": td_last_year,
                                            "format": "yyyy-MM-dd HH:mm:ss",
                                            "time_zone": self.ds_tz_calculate
                                        }
                                    }
                                },
                                {
                                    "range": {
                                        "sale_date": {
                                            "gte": fd_current_year,
                                            "lte": td_current_year,
                                            "format": "yyyy-MM-dd HH:mm:ss",
                                            "time_zone": self.ds_tz_calculate
                                        }
                                    }
                                }
                            ],
                            "minimum_should_match": 1
                        }
                    }
                ]
            }
        }

        if modified_filter:
            filter_cond["bool"]["must"].append(
                {
                    "range": {
                        "modified": {
                            "gte": modified_filter,
                            "format": "yyyy-MM-dd HH:mm:ss",
                            "time_zone": self.ds_tz_calculate
                        }
                    }
                }
            )

        query = {
            "size": 0,
            "query": filter_cond,
            "aggs": {
                "unique_combinations": {
                    "cardinality": {
                        "script": {
                            "source": "doc['parent_asin.keyword'].value + '|' "
                                      "+ doc['product_number.keyword'].value + '|' "
                                      "+ doc['product_type.keyword'].value + '|' "
                                      "+ doc['title.keyword'].value",
                            "lang": "painless"
                        }
                    }
                }
            }
        }
        # print(query)
        res = analysis_es_service.search(query=query)
        count = res["aggregations"]["unique_combinations"]["value"]
        return count
