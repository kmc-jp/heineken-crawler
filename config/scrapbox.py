import os

SCRAPBOX_ENDPOINT = "https://scrapbox.io/"
SCRAPBOX_PROJECT = "kmc"
SCRAPBOX_CONNECT_SID = os.getenv("SCRAPBOX_CONNECT_SID")
ELASTIC_SEARCH_ENDPOINT = os.getenv("ELASTIC_SEARCH_ENDPOINT", "http://heineken-elasticsearch.default.svc.cluster.local:9200/")
INDEX = "scrapbox"
INDEX_FILE = "index/scrapbox.json"
