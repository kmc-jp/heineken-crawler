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
    all_query = {
            "sort": { "modified": "desc" },
            "query": {"match_all": {}},
            "_source": ["modified"],
            # els size limit
            # TODO: paging
            "size": 10000
            }

    all_entries = json.loads(
            client.search(json.dumps(all_query)).read().decode("utf-8")
            )
    if all_entries["hits"]["total"] > 0:
        last_modified = all_entries["hits"]["hits"][0]["_source"]["modified"]
    else:
        last_modified = 0

    els_ids = set(map(lambda x: x["_id"], all_entries["hits"]["hits"]))

    paths = glob.glob(os.path.join(config.PUKIWIKI_DATA_DIR, "*.txt"))

    # modified paths or not exist paths (e.g. rename)
    modified_paths = list(filter(
        lambda x: int(os.path.getmtime(x) * 1000) > last_modified
            or not _get_filename(x) in els_ids
            , paths
        ))

    if modified_paths:
        bulk_string = "\n".join(
                _create_page_json_for_bulk(_get_page_data(x)) for x in modified_paths
                ) + "\n"
        client.bulk(bulk_string)

    filenames = list(map(_get_filename, paths))
    # delete deleted pages by pukiwiki
    deleted_page_query = {
            "query": {
                "bool": {
                    "must_not": {
                        "terms": {
                            "_id": filenames
                            }
                        }
                    }
                },
            "_source": ["title"]
            }
    client.delete_by_query(json.dumps(deleted_page_query))

def _create_page_json_for_bulk(data):
    # use filename as _id
    head = json.dumps({"index" : { "_index": config.INDEX, "_type": config.TYPE, "_id": data.pop("filename") }})
    return head + "\n" + json.dumps(data)


def _get_page_data(path):
    filename = _get_filename(path)
    title = _get_page_title(filename)
    title_url_encoded = urllib.parse.quote(
            # includes '/' for encode
            title, encoding="euc-jp", safe=''
            )
    modified = int(os.path.getmtime(path) * 1000)

    with open(path, encoding="euc-jp", errors='replace') as f:
        body = f.read()

    return {
            "body": body,
            "title": title,
            "title_url_encoded": title_url_encoded,
            "modified": modified,
            "filename": filename
            }

def _get_page_title(filename):
    # euc-jp encode <- pukiwiki hex title
    #
    # e.g. "あいう" -> euc-jp: 0xA4 0xA2 0xA4 0xA4 0xA4 0xA6
    #               -> pukiwiki: A4A2A4A4A4A6.txt
    return bytes.fromhex(filename).decode("euc-jp")

def _get_filename(path):
    # remove '.txt'
    return os.path.basename(path)[:-4]

crawl()
