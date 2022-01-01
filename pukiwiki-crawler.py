import urllib.parse
import os
from functools import reduce
from datetime import date
import time
import argparse

import json
import glob
import urllib.request
import urllib.parse

from els.client import ElsClient

from config import pukiwiki as config

client = ElsClient(config.ELASTIC_SEARCH_ENDPOINT, config.INDEX)

def add_index(args):
    with open(config.INDEX_FILE) as f:
        client.add_index(f.read())


def delete_index(args):
    client.delete_index()


def crawl(args):
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
    if all_entries["hits"]["total"]["relation"] in ("gte", "eq") and all_entries["hits"]["total"]["value"] > 0:
        last_modified = all_entries["hits"]["hits"][0]["_source"]["modified"]
    else:
        last_modified = 0

    els_ids = set(map(lambda x: x["_id"], all_entries["hits"]["hits"]))

    paths = glob.glob(os.path.join(config.PUKIWIKI_DATA_DIR, "*.txt"))

    # modified paths or not exist paths (e.g. rename)
    modified_paths = list(filter(
        # ctime is always updated unlike mtime
        lambda x: int(os.path.getctime(x) * 1000) > last_modified
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
    head = json.dumps({"index" : { "_index": config.INDEX, "_id": data.pop("filename") }})
    return head + "\n" + json.dumps(data)


def _get_page_data(path):
    filename = _get_filename(path)
    title = _get_page_title(filename)
    title_url_encoded = urllib.parse.quote(
            # includes '/' for encode
            title, safe=''
            )
    modified = int(os.path.getctime(path) * 1000)

    with open(path, errors='replace') as f:
        body = f.read()

    return {
            "body": body,
            "title": title,
            "title_url_encoded": title_url_encoded,
            "modified": modified,
            "filename": filename
            }

def _get_page_title(filename):
    # utf-8 encode <- pukiwiki hex title
    #
    # e.g. "練習会" -> utf-8: \xE7\xB7\xB4\xE7\xBF\x92\xE4\xBC\x9A
    #               -> pukiwiki: E7B7B4E7BF92E4BC9A.txt
    return bytes.fromhex(filename).decode("utf-8")

def _get_filename(path):
    # remove '.txt'
    return os.path.basename(path)[:-4]

parser = argparse.ArgumentParser(description='PukiWiki crawler for elasticsearch')
subparsers = parser.add_subparsers()

parser_add = subparsers.add_parser('add-index', help='add index')
parser_add.set_defaults(func=add_index)

parser_add = subparsers.add_parser('delete-index', help='delete index')
parser_add.set_defaults(func=delete_index)

parser_crawl = subparsers.add_parser('crawl', help='crawl')
parser_crawl.set_defaults(func=crawl)

args = parser.parse_args()
if hasattr(args, 'func'):
    args.func(args)
else:
    parser.print_help()
