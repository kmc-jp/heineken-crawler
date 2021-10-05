# heineken-crawler

Hayai Kensaku Pukiwiki Crawler & Client

Jenkins: https://inside.kmc.gr.jp/jenkins/job/heineken-crawler/

## Requirements

Python 3.x

## Usage

#### PukiWiki

- Setup

```shell
$ poetry install
$ edit config/pukiwiki.py
```

- Crawl

```shell
$ poetry run python3 pukiwiki-crawler.py crawl
```

- Create index

```shell
$ poetry run python3 pukiwiki-crawler.py add-index
```

- Clients for dev

```shell
# show help
$ poetry run python3 dev-client.py -h
```

#### Mail (Paragate)

- Setup

```shell
$ edit config/paragate.py
```

- Crawl

```shell
$ poetry run python3 paragate-crawler.py crawl
```

- Create index

```shell
$ poetry run python3 paragate-crawler.py add-index
```

## Words

- els => elastic search

## License

See [LICENSE](./LICENSE)
