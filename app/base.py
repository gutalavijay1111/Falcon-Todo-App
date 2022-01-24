import falcon
import json
from .errors import *

class BaseResource(object):
    WELCOME_MESSAGE = {
        "message": "Welcome to ToDo App, Please login to continue!"
    }

    def to_json(self, data):
        return json.dumps(data, default=str)

    def on_get(self, req, resp):
        if req.path == "/":
            resp.status = falcon.HTTP_200
            resp.body = self.to_json(self.WELCOME_MESSAGE)
        else:
            raise MethodNotSupportedError(method="GET", url=req.path)

    def on_post(self, req, resp):
        raise MethodNotSupportedError(method="POST", url=req.path)

    def on_put(self, req, resp):
        raise MethodNotSupportedError(method="PUT", url=req.path)

    def on_delete(self, req, resp):
        raise MethodNotSupportedError(method="DELETE", url=req.path)