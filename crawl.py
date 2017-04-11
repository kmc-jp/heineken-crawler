import urllib.parse
import os
from functools import reduce
from datetime import date

import json
import glob
import urllib.request
import urllib.parse

import config

def crawl():
    # TODO: 差分のみ
    paths = glob.glob(os.path.join(PUKIWIKI_DATA_DIR, "*.txt"))
    bulk_string = reduce(lambda x, y: x + "\n" + y,
            map(lambda x: _get_page_json_for_bulk(_get_page_data(x)), paths)
            )


    req = urllib.request.Request(
            urllib.parse.urljoin(ELASTIC_SEARCH_ENDPOINT, "/_bulk"),
            data=bulk_string.encode("utf8"), 
            headers={'content-type': 'application/json'}
            )

    try:
        urllib.request.urlopen(req)
    except Exception as e:
        print(e.read())

def _get_page_json_for_bulk(data):
    head = json.dumps({"index" : { "_index": INDEX, "_type": TYPE }})
    return head + "\n" + json.dumps(data)


def _get_page_data(path):
    title = _get_page_title(path)
    modified = int(os.path.getmtime(path) * 1000)

    with open(path, encoding="euc-jp", errors='replace') as f:
        body = f.read()

    return {
            "body": body,
            "title": title,
            "modified": modified
            }

def _get_page_title(path):
    # remove '.txt'
    filename = os.path.basename(path)[:-4]

    # euc-jp encode <- pukiwiki hex title
    #
    # e.g. "あいう" -> euc-jp: 0xA4 0xA2 0xA4 0xA4 0xA4 0xA6
    #               -> pukiwiki: A4A2A4A4A4A6.txt
    return bytes.fromhex(filename).decode("euc-jp")

crawl()
