import flask


class RequestDictionary(dict):
    def __init__(self, *args, default_val=None, **kwargs):
        self.default_val = default_val
        super().__init__(*args, **kwargs)

    def __getattr__(self, key):
        return self.get(key, self.default_val)


def create(default_val=None, **route_args) -> RequestDictionary:
    request = flask.request

    data = {
        **request.args,  # The Key/Value pairs in the URL query string
        **request.headers,  # Header values
        **request.form,  # The key/value pairs in the body, from an HTML port form
        **route_args,  # Additional arguments the method can access
    }
    for k, v in data.items():
        if isinstance(v, list) and len(v) == 1:
            data[k] = v[0]

    return RequestDictionary(data, default_val=default_val)
