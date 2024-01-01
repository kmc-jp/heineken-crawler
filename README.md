# heineken-crawler

Hayai Kensaku Pukiwiki Crawler & Client

## Requirements

Python 3.x

## Usage

You can also use [Docker image](https://github.com/kmc-jp/heineken-crawler/pkgs/container/heineken-crawler). Entrypoint is `poetry run python3`.

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

#### Scrapbox

- Setup

```shell
$ edit config/scrapbox.py
```

`SCRAPBOX_CONNECT_SID` はブラウザの開発者ツールから `cookie[connect.sid]` を取得してください。

- Crawl

```shell
$ poetry run python3 scrapbox-crawler.py crawl
```

- Create index

```shell
$ poetry run python3 scrapbox-crawler.py add-index
```

## Tips

To access dev app in kubernetes...

```
$ kubectl port-forward service/{svc name} 9200:9200
```

## Words

- els => elastic search

## License

See [LICENSE](./LICENSE) for license and [DOCKER_NOTICE](./DOCKER_NOTICE) for Docker image notices.
