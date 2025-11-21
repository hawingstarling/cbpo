def get_label(key: str) -> str:
    # sensitive keyword UI
    message = {
        "amazon_scraping": "Investigate seller prices on Amazon",
        "amazon_inventory_scraping": "Investigate inventory of Amazon sellers",
        "google_scraping": "Investigate seller prices on Google Shopping",
    }
    return message.get(key, key.replace("_", " "))


def parse_key_value_label(key: str, value) -> dict:
    return {"key": key, "value": value}
