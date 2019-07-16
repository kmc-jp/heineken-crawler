# heineken-crawler

Hayai Kensaku Pukiwiki Crawler & Client

Jenkins: https://inside.kmc.gr.jp/jenkins/job/heineken-crawler/

## Requirements

Python 3.x

## Usage

#### PukiWiki

- Setup

```shell
$ pipenv install
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
