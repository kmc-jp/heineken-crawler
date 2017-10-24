import urllib.parse
import os
from datetime import datetime
import argparse
import email
from email import policy, utils
import json
import itertools
import traceback

from bs4 import BeautifulSoup

from els.client import ElsClient
from config import paragate as config

client = ElsClient(config.ELASTIC_SEARCH_ENDPOINT, config.INDEX)

def add_index(args):
    with open(config.INDEX_FILE) as f:
        client.add_index(f.read())

def crawl(args):
    categories = _get_categories()

    mail_jsons = []
    for category in categories:
        els_latest = _get_els_latest_index(category)
        local_latest = _get_local_latest_index(category)

        for index in range(els_latest, local_latest):
            print(category)
            print(index)
            try:
                mail_jsons.append(_create_mail_json(category, index))
            except:
                traceback.print_exc()

            if len(mail_jsons) > 300:
                bulk_string = "\n".join(
                    _create_json_for_bulk(x) for x in mail_jsons
                        ) + "\n"
                client.bulk(bulk_string)
                mail_jsons = []


def _get_categories():
    base = config.PARAGATE_MAIL_DIR
    # Check index file
    return [p for p in os.listdir(base) if os.path.isfile(os.path.join(base, p, 'index'))]

def _get_local_latest_index(category):
    index_file = os.path.join(config.PARAGATE_MAIL_DIR, category, 'index')
    with open(index_file) as f:
        return int(f.read())

def _get_els_latest_index(category):
    # Fetch last mail per category
    query = {
            "query": {
                "bool": {"must": {"term": {"category": category}}}
                },
            "sort": {"index": "desc"},
            "_source": ["index"],
            "size": 1,
            }

    result =  json.loads(
            client.search(json.dumps(query)).read().decode('utf-8')
            )

    if result['hits']['total'] == 0:
        return -1
    else:
        return result['hits']['hits'][0]['_source']['index']

def _extract_subject(message):
    try:
        return message['subject']
    except:
        return None

def _create_mail_json(category, index):
    path = os.path.join(config.PARAGATE_MAIL_DIR, category, str(index))

    message = None
    with open(path, 'rb') as f:
        message = email.message_from_binary_file(f, policy=email.policy.default)

    content = _extract_content(message) or '(NO CONTENT)'
    subject = _extract_subject(message) or '(NO SUBJECT)'

    from_addr = _extract_from_addr(message)
    assert(from_addr)

    recipient_addrs = _extract_recipient_addrs(message)
    assert(recipient_addrs)

    date = _extract_date(message)
    assert(date)

    message = {
            'category': category,
            'index': index,
            'from': from_addr,
            'to': recipient_addrs,
            'subject': subject,
            'date': int(date.timestamp() * 1000),
            'body': content,
            }

    return message

def _ensure_charset(message):
    if not message.get_content_charset():
        message.set_charset('utf-8')

def _extract_content(message):
    plain_message = message.get_body(preferencelist=('plain', ))

    if plain_message:
        _ensure_charset(plain_message)
        content = plain_message.get_content()
    else:
        html_message = message.get_body(preferencelist=('html', ))

        if not html_message: return None

        _ensure_charset(html_message)
        soup = BeautifulSoup(html_message.get_content(), 'lxml')
        # Remove unused elements
        for elem in soup.findAll(['script', 'style']):
            elem.extract()

        body = soup.body
        if body:
            # lxml usually adds body tag automatically
            content = body.get_text()
        else:
            content = soup.get_text()

    # Multi lines / spaces to single space
    return " ".join(content.split())

def _extract_from_addr(message):
    # Ignore realname
    from_addr = None
    try:
        from_addr = email.utils.parseaddr(message['from'])[1]
    except:
        pass

    if not from_addr:
        # Some mails have no from header or invalid from header
        #
        # no from header -> return None
        # invalid from header -> throw Exception
        #
        # -> Use Unix header
        # e.g.
        # 'From foo@example.com Fri Jul  2 21:55:16 2010'
        from_addr = message.get_unixfrom().split()[1]

    return from_addr

def _extract_recipient_addrs(message):
    # Merge to, cc, bcc, delivered-to
    recipients = []
    for key in ['to', 'cc', 'bcc', 'x-original-to', 'reply-to']:
        try:
            recipients += message.get_all(key)
        except:
            pass

    # Ignore realname and invalid address
    return list(
            filter(bool, set(x[1] for x in email.utils.getaddresses(recipients)))
            )

def _extract_date(message):
    try:
        return email.utils.parsedate_to_datetime(message['date'])
    except:
        # Some mails have not date header or invalid date header
        # -> Use Unix header
        # e.g.
        # 'From foo@example.com Fri Jul  2 21:55:16 2010'
        maybe_date = ' '.join(message.get_unixfrom().split()[-5:])
        return datetime.strptime(maybe_date, '%a %b %d %H:%M:%S %Y')

def _create_json_for_bulk(data):
    # Use filename as _id
    head = json.dumps({
        "index": {
            "_index": config.INDEX,
            "_type": config.TYPE,
            "_id": "{0}/{1}".format(data['category'], data['index'])
            }
        })
    return head + "\n" + json.dumps(data)

parser = argparse.ArgumentParser(description='Paragate (mail) crawler for elasticsearch')
subparsers = parser.add_subparsers()

parser_add = subparsers.add_parser('add-index', help='add index')
parser_add.set_defaults(func=add_index)

parser_crawl = subparsers.add_parser('crawl', help='crawl')
parser_crawl.set_defaults(func=crawl)

args = parser.parse_args()
if hasattr(args, 'func'):
    args.func(args)
else:
    parser.print_help()
