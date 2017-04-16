# これはなに

JSON にはコメントが書けないからここにメモを書くよ


# 解説

- エラサーは json で index を定義する


### 設定

``` json
  "settings": {
    "analysis": {
      "analyzer": {
        "jp_analyzer": {
          "tokenizer": "jp_tokenizer",
          "char_filter": [
            "html_strip", "icu_normalizer"
          ],
          "filter": []
        }
      },

      "tokenizer": {
        "jp_tokenizer": {
          "type": "ngram",
          "min_gram": 2,
          "max_gram": 3,
          "token_chars": [
            "letter", "digit", "symbol", "punctuation"
          ]
        }
      }
    }
  },
```

ここには index の設定が入る。 

- tokenizer には `jp_tokenizer` を定義していて、n-gram を使っている。 n-gram なので検索に漏れがない。
- `token_chars` に記号を含めているので記号にもヒットする。
- `char_filter` は `tokenizer` に入れる前にフィルタリングする。
  - `html_strip` は HTML タグを除く。
  - `icu_normalizer` は日本語のノーマライザで、ひらがな・カタカナの調整をする。また、case insensitive にもしてくれる。

# mapping

```json
  "mappings": {
    "page": {
      "_all": { "enabled": false },
      "properties": {
        "title": {
          "type": "text",
          "analyzer": "jp_analyzer",
          "term_vector" : "with_positions_offsets"
        },
        "title_url_encoded": {
          "type": "keyword",
          "index": false
        },
        "body": {
          "type": "text",
          "analyzer": "jp_analyzer",
          "term_vector" : "with_positions_offsets"
        },
        "modified": {
          "type": "date",
          "format": "epoch_millis"
        }
      }
    }
  }
```

いわゆる型のようなもの。

- highlight (検索結果の語彙のハイライト) のために `term_vector` を `with_positions_offsets` にしている。
    - これで highlight が早くなる + 良くなる
- js で euc-jp エンコードは出来ないので crawler 側で `title_url_encoded` に突っ込んでいる。
- `_all` を用いると全カラム検索ができるが不要なのでオフ。
