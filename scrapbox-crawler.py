import argparse
import json
import urllib.parse
import urllib.request
from urllib.error import HTTPError
import requests
from datetime import datetime
import time

from config import scrapbox as config
from els.client import ElsClient
import logging

INTERVAL_SEC = 1
BULK_SIZE = 30

client = ElsClient(config.ELASTIC_SEARCH_ENDPOINT, config.INDEX)

fmt = "%(asctime)s %(levelname)s %(name)s :%(message)s"
logging.basicConfig(level=logging.INFO, format=fmt)
logger = logging.getLogger(__name__)

def add_index(args):
    # Add index if not exists
    try:
        client.get_index()
    except HTTPError as e:
        if e.status == 404:
            with open(config.INDEX_FILE) as f:
                logger.info(client.add_index(f.read()).read().decode("utf-8"))
        else:
            raise


def delete_index(args):
    logger.info(client.delete_index().read().decode("utf-8"))


def crawl(args):
    cookies = {"connect.sid": config.SCRAPBOX_CONNECT_SID}
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


    modified_page_titles = []
    offset=0
    logger.info("start list pages")
    while True:
        params = {"skip": offset, "limit": 100, "sort": "modified"}       
        response = requests.get(urllib.parse.urljoin(config.SCRAPBOX_ENDPOINT, f'/api/pages/{config.SCRAPBOX_PROJECT}'), cookies=cookies, params=params)
        response.raise_for_status()
        raw_pages = response.json()
            
        
        if raw_pages["pages"]:
            for page in raw_pages["pages"]:
                isRequireUpdate = page["updated"] > last_modified or page["id"] not in els_ids
                if isRequireUpdate:
                    modified_page_titles.append(page["title"]) 

        # 一番最後のpageが更新されていなければ、次ページの探索をやめる
        if raw_pages["pages"][-1]["title"] != modified_page_titles[-1]:
            break
        offset += 100
        if offset > raw_pages["count"]:
            break
    
    logger.info("number of modified pages: "+str(len(modified_page_titles)))

    if len(modified_page_titles) > 0:
        # BULK_SIZE個ずつbulk createする
        for i in range(0, len(modified_page_titles), BULK_SIZE):
            logger.info(f"start bulk create: {i} - {i+BULK_SIZE} / {len(modified_page_titles)}")
            bulk_string = "\n".join(_create_page_json_for_bulk(_get_page_data(cookies, x)) for x in modified_page_titles[i:i+100]) + "\n"
            logger.info(client.bulk(bulk_string).read().decode("utf-8"))

    # streamのeventから削除対象ページを取得
    response = requests.get(urllib.parse.urljoin(config.SCRAPBOX_ENDPOINT, f"/api/stream/{config.SCRAPBOX_PROJECT}"), cookies=cookies)
    response.raise_for_status()
    raw_stream = response.json()
    deleted_page_ids =[]
    for stream in raw_stream:
        if stream["type"] == "page.delete" and stream["id"] in els_ids and stream["id"] not in deleted_page_ids:
            deleted_page_ids.append(stream["id"])

    if len(deleted_page_ids) > 0:
        deleted_page_query = {
                "query": {
                    "bool": {
                        "must_not": {
                            "terms": {
                                "_id": deleted_page_ids
                                }
                            }
                        }
                    },
                "_source": ["title"]
                }
        logger.info(client.delete_by_query(json.dumps(deleted_page_query)).read().decode("utf-8"))
    
def _create_page_json_for_bulk(data):
    head = json.dumps({"index" : { "_index": config.INDEX, "_id": data.pop("_id") }})
    return head + "\n" + json.dumps(data)

def _get_page_data(cookies, page_title):
    # デフォルトで/はエンコードされないので、safe=''を指定する
    url = urllib.parse.urljoin(config.SCRAPBOX_ENDPOINT, f"/api/pages/{config.SCRAPBOX_PROJECT}/{urllib.parse.quote(page_title, safe='')}")
    response = requests.get(url, cookies=cookies)
    response.raise_for_status()
    page = response.json()
    time.sleep(INTERVAL_SEC)
    logger.info("fetched: "+url)
    return {
        "_id": page["id"],
        "title": page["title"],
        "body": "\n".join(x["text"] for x in page["lines"]),
        "modified": page["updated"]
        }

parser = argparse.ArgumentParser(description='Scrapbox crawler for elasticsearch')
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
