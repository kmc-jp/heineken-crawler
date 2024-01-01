[共通部分は pukiwiki 参照](./pukiwiki-memo.md)

### 設定

# mapping

```json
  "mappings": {
   "properties": {
      "title": {
         "type": "text",
         "analyzer": "jp_analyzer",
         "term_vector" : "with_positions_offsets",
         "fields": {
         "keyword": { "type": "keyword" }
         }
      },
      "body": {
         "type": "text",
         "analyzer": "jp_analyzer",
         "term_vector" : "with_positions_offsets"
      },
      "modified": {
         "type": "date",
         "format": "strict_date_optional_time||epoch_millis"
      }
    }
  }
```

- ほとんど pukiwiki と一緒
