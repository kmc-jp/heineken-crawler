import os

# dir includes wiki raw data
PUKIWIKI_DATA_DIR = os.getenv("HEINEKEN_CRAWLER_PUKIWIKI_PUKIWIKI_DATA_DIR", "data/wiki")
ELASTIC_SEARCH_ENDPOINT = os.getenv("HEINEKEN_CRAWLER_PUKIWIKI_ELASTIC_SEARCH_ENDPOINT", "http://localhost:9200/")
INDEX = "pukiwiki"
INDEX_FILE = "index/pukiwiki.json"
