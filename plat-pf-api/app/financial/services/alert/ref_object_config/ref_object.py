ref_object_template = {
    "q": {
        "base": {
            "config": {
                "query": {}
            }
        },
        "form": {
            "config": {
                "query": {},
                "controls": []
            }
        },
        "builder": {
            "config": {
                "form": {
                    "columns": []
                },
                "modal": {
                    "title": "Query Builder"
                },
                "query": {},
                "format": {
                    "temporal": {
                        "date": {
                            "type": "date",
                            "formatLabel": "MM/DD/YYYY",
                            "formatValue": "YYYY-MM-DD"
                        },
                        "datetime": {
                            "type": "datetime",
                            "formatLabel": "MM/DD/YYYY hh:mm:ss A",
                            "formatValue": "YYYY-MM-DDTHH:mm:ss"
                        }
                    }
                },
                "ignore": {
                    "base": {
                        "value": True,
                        "visible": True
                    },
                    "global": {
                        "value": False,
                        "visible": False
                    }
                },
                "trigger": {
                    "label": "Setting Filter"
                },
                "threshold": {
                    "maxLevel": 5
                },
                "hiddenColumns": []
            },
            "enabled": True,
            "readable": {
                "enabled": False
            },
            "enabledFilterReadable": False
        },
        "alignment": "",
        "globalFilter": {
            "enabled": False
        }
    },
    "currentView": "SALE_ITEMS"
}
