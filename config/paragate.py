import os

# dir includes wiki raw data
PARAGATE_MAIL_DIR = os.getenv("HEINEKEN_CRAWLER_PARAGATE_PARAGATE_MAIL_DIR", "data/mail")
ELASTIC_SEARCH_ENDPOINT = os.getenv("HEINEKEN_CRAWLER_PARAGATE_ELASTIC_SEARCH_ENDPOINT", "http://localhost:9200/")
INDEX = "mail"
INDEX_FILE = "index/mail.json"
