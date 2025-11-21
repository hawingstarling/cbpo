from app.es.variables.mapping_types.config import ES_TEXT_TYPE, ES_MAPPING_TYPE_FIELDS_CONFIG

ES_TIMEOUT = 30
ES_TIME_SLEEP = 2
ES_BULK_SIZE = 1000
ES_QUEUE_LIMIT = 10000
ES_MAX_RETRY = 1

#
ES_UPSERT_ACTION = "upsert"
ES_UPDATE_ACTION = "update"
ES_DELETE_ACTION = "delete"
ACTIONS_TYPE = [ES_UPDATE_ACTION, ES_UPSERT_ACTION, ES_DELETE_ACTION]

#
ELASTICSEARCH_INDEX_SETTING_DEFAULT = {
    "settings": {
        "index": {
            "max_ngram_diff": "48",
            "max_result_window": "1000000"
        },
        "analysis": {
            "filter": {
                "mynGram": {
                    "type": "ngram",
                    "min_gram": "2",
                    "max_gram": "50"
                }
            },
            "analyzer": {
                "analyzer_startswith": {
                    "tokenizer": "keyword",
                    "filter": "lowercase"
                },
                "analyzer_endswith": {
                    "tokenizer": "keyword",
                    "filter": [
                        "lowercase",
                        "reverse"
                    ]
                },
                "whitespace": {
                    "type": "custom",
                    "filter": [
                        "trim",
                        "lowercase"
                    ],
                    "tokenizer": "whitespace"
                },
                "ngram_analyzer": {
                    "tokenizer": "ngram_tokenizer",
                    "filter": "lowercase"
                },
                "special_analyzer": {
                    "type": "pattern",
                    "tokenizer": "keyword",
                    "pattern": "\\n|\\s|\\t|\\r",
                    "filter": [
                        "trim",
                        "lowercase",
                        "mynGram"
                    ]
                }
            },
            "tokenizer": {
                "ngram_tokenizer": {
                    "type": "ngram",
                    "token_chars": [
                        "letter",
                        "digit",
                        "whitespace",
                        "punctuation",
                        "symbol"
                    ]
                }
            }
        }
    },
    "mappings": {
        "dynamic_templates": [
            {
                "texts_engine": {
                    "match_mapping_type": "string",
                    "mapping": {
                        "type": ES_TEXT_TYPE,
                        "norms": True,
                        "analyzer": "special_analyzer",
                        "fields": ES_MAPPING_TYPE_FIELDS_CONFIG[ES_TEXT_TYPE]
                    }
                }
            }
        ]
    }
}
