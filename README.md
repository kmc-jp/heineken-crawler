# heineken-crawler

Hayai Kensaku Pukiwiki Crawler & Client

## Requirements

Python 3.x

## Usage

#### PukiWiki

- Setup

```shell
$ pipenv install
$ cp config/pukiwiki.py.example config/pukiwiki.py
$ edit config/pukiwiki.py
```

- Crawl

```shell
$ pipenv run python3 pukiwiki-crawler.py crawl
```

- Create index

```shell
$ pipenv run python3 pukiwiki-crawler.py add-index
```

- Clients for dev

```shell
# show help
$ pipenv run python3 dev-client.py -h
```

#### Mail (Paragate)

- Setup

```shell
$ cp config/paragate.py.example config/paragate.py
$ edit config/paragate.py
```

- Crawl

```shell
$ pipenv run python3 paragate-crawler.py crawl
```

- Create index

```shell
$ pipenv run python3 paragate-crawler.py add-index
```

## Words

- els => elastic search
