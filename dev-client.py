import argparse
import config
import json

from els.client import ElsClient

client = ElsClient(config.ELASTIC_SEARCH_ENDPOINT, config.INDEX)

def add_index(args):
    with args.index_file as f:
        client.add_index(f.read())

def delete_index(args):
    client.delete_index(index=args.index)

def search(args):
    query = {
            "query": {
                "query_string": {
                    # boost title
                    "fields": ["title^5", "body"],
                    "query": args.query,
                    "auto_generate_phrase_queries": True
                    }
                }
            }
    if args.title: query["_source"] = ["title"]
    if args.explain: query["explain"] = True

    body = client.search(json.dumps(query)).read().decode("utf-8")
    print(body)

parser = argparse.ArgumentParser(description='Elastic search client')
subparsers = parser.add_subparsers()

parser_add = subparsers.add_parser('add-index', help='add index (see add-index -h)')
parser_add.add_argument('index_file', type=argparse.FileType(), help='index config json file')
parser_add.set_defaults(func=add_index)

parser_delete = subparsers.add_parser('delete-index', help='delete index (see delete-index -h)')
parser_delete.add_argument(
        '-i',
        '--index', 
        default=config.INDEX,
        type=str,
        help="index for delete (default: %(default)s)"
        )
parser_delete.set_defaults(func=delete_index)

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
parser_search.set_defaults(func=search)

args = parser.parse_args()
if hasattr(args, 'func'):
    args.func(args)
else:
    parser.print_help()
