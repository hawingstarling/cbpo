FIELD_TEXT_CONFIG = {
    "keyword": {
        "type": "keyword",
        "ignore_above": 256
    },
    "raw": {
        "type": "text",
        "analyzer": "whitespace",
        "fielddata": True
    },
    "starts_with": {
        "type": "text",
        "analyzer": "analyzer_startswith",
        "fielddata": True
    },
    "ends_with": {
        "type": "text",
        "analyzer": "analyzer_endswith",
        "fielddata": True
    }
}
