[共通部分は pukiwiki 参照](./pukiwiki-memo.md)


### 設定


# mapping

```json
  "mappings": {
    "message": {
      "_all": { "enabled": false },
      "properties": {
        "subject": {
          "type": "text",
          "analyzer": "jp_analyzer"
        },
        "from": {
          "type": "text",
          "analyzer": "standard"
        },
        "to": {
          "type": "text",
          "analyzer": "standard"
        },
        "content": {
          "type": "text",
          "analyzer": "jp_analyzer",
          "term_vector" : "with_positions_offsets"
        },
        "date": {
          "type": "date",
          "format": "strict_date_optional_time||epoch_millis"
        }
      }
    }
  }
```

- メールアドレスはマッチング精度を高めるために simple にしている。
  - アドレスを検索するときは単語単位であることが多いだろうという推測
  - `@` などの記号は消えるので完全マッチでの検索はできない
    - 将来その需要が生まれた場合、keyword を追加するか記号も index に入れると良い
  - 差出人名はここに入れない.
    - `fugafuga <hoge@example.com>` の `fugafuga`
