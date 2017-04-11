import urllib.parse
import os
from functools import reduce
from datetime import date
import time

import json
import glob
import urllib.request
import urllib.parse

from els.client import ElsClient

import config

client = ElsClient(config.ELASTIC_SEARCH_ENDPOINT, config.INDEX)

def crawl():
    # TODO: deleted pages
    # TODO: use api
    data = os.path.join(os.path.dirname(__file__), "data")

    data_file_path = os.path.join(data, "last_crawled_time")

    if os.path.exists(data_file_path):
        with open(data_file_path) as f:
            last_crawled = float(f.read())
    else:
        os.makedirs(data, exist_ok=True)
        last_crawled = 0

    paths = glob.glob(os.path.join(config.PUKIWIKI_DATA_DIR, "*.txt"))
    modified_paths = list(filter(lambda x: os.path.getmtime(x) > last_crawled, paths))

    if modified_paths:
        bulk_string = "\n".join(
                _create_page_json_for_bulk(_get_page_data(x)) for x in modified_paths
                )
        client.bulk(bulk_string)

    with open(data_file_path, "w") as f:
        f.write(str(time.time()))

def _create_page_json_for_bulk(data):
    # use filename as _id
    head = json.dumps({"index" : { "_index": config.INDEX, "_type": config.TYPE, "_id": data.pop("filename") }})
    return head + "\n" + json.dumps(data)


def _get_page_data(path):
    # remove '.txt'
    filename = os.path.basename(path)[:-4]
    title = _get_page_title(filename)
    modified = int(os.path.getmtime(path) * 1000)

    with open(path, encoding="euc-jp", errors='replace') as f:
        body = f.read()

    return {
            "body": body,
            "title": title,
            "modified": modified,
            "filename": filename
            }

def _get_page_title(filename):
    # euc-jp encode <- pukiwiki hex title
    #
    # e.g. "あいう" -> euc-jp: 0xA4 0xA2 0xA4 0xA4 0xA4 0xA6
    #               -> pukiwiki: A4A2A4A4A4A6.txt
    return bytes.fromhex(filename).decode("euc-jp")

crawl()
