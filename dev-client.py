import argparse
import json

from config import pukiwiki
from els.client import ElsClient

client = ElsClient(pukiwiki.ELASTIC_SEARCH_ENDPOINT, pukiwiki.INDEX)

def search(args):
    query = {
            "query": {
                "query_string": {
                    # boost title
                    "fields": ["title^5", "body"],
                    "query": args.query,
                    # "analyzer": "jp_search_analyzer",
                    "default_operator": "AND",
                    # "type": "phrase",
                    }
                }
            }
    if args.title: query["_source"] = ["title"]
    if args.explain:
        query["explain"] = True
        query["profile"] = True
    if args.highlight:
        query["highlight"] = {
            "encoder": "html",
            "fields": {
                "body": {
                    "pre_tags": ["<mark>"],
                    "post_tags": ["</mark>"],
                    "fragment_size": 220,
                    "no_match_size": 220,
                    "number_of_fragments": 1,
                }
            }
        }

    body = client.search(json.dumps(query)).read().decode("utf-8")
    print(body)

parser = argparse.ArgumentParser(description='Elastic search client')
subparsers = parser.add_subparsers()

parser_search = subparsers.add_parser('search', help='search (see search -h)')
parser_search.add_argument('query', type=str, help='search query')
parser_search.add_argument(
        '-t',
        '--title',
        action="store_true",
        help="return title only"
        )
parser_search.add_argument(
        '-e',
        '--explain',
        action="store_true",
        help="include explain"
        )
parser_search.add_argument(
        '--highlight',
        action="store_true",
        help="include highlight"
        )
parser_search.set_defaults(func=search)

args = parser.parse_args()
if hasattr(args, 'func'):
    args.func(args)
else:
    parser.print_help()
