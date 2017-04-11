import urllib.request
import urllib.parse

class ElsClient:
    def __init__(self, endpoint, index):
        self.endpoint = endpoint
        self.index = index

    def add_index(self, index_json_string, index=None):
        if not index: index = self.index

        req = urllib.request.Request(
                urllib.parse.urljoin(self.endpoint, "/" + self.index),
                data=index_json_string.encode("utf8"),
                headers={'content-type': 'application/json'},
                method="PUT"
                )
        return self._request(req)

    def delete_index(self, index=None):
        if not index: index = self.index

        req = urllib.request.Request(
                urllib.parse.urljoin(self.endpoint, "/" + index),
                method="DELETE"
                )
        return self._request(req)


    def bulk(self, bulk_string):
        req = urllib.request.Request(
                # response after refresh -> ?refresh=wait_for
                urllib.parse.urljoin(self.endpoint, "/_bulk"),
                data=bulk_string.encode("utf8"),
                headers={'content-type': 'application/json'},
                method="POST"
                )
        return self._request(req)

    def search(self, search_json_string):
        req = urllib.request.Request(
                # response after refresh -> ?refresh=wait_for
                urllib.parse.urljoin(
                    self.endpoint,
                    "{0}/_search".format(self.index)
                    ),
                data=search_json_string.encode("utf8"),
                headers={'content-type': 'application/json'},
                method="GET"
                )
        return self._request(req)

    def _request(self, req):
        try:
            return urllib.request.urlopen(req)
        except Exception as e:
            print(e.read())
            raise
