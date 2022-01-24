import falcon
from urllib.request import urlcleanup
import json


BASE_ERROR = {
    "status" : falcon.HTTP_500,
    "title": "Somethig went wrong"
}

METHOD_NOT_SUPPORTED = {
    "status" : falcon.HTTP_404,
    "title": "Method not Supported"
}

USER_DOES_NOT_EXIST = {
    "status" : falcon.HTTP_404,
    "title": "User doesnot exist"
}

PASSWORD_MISMATCH = {
    "status" : falcon.HTTP_404,
    "title": "Password Mismatch"
}

ERR_USER_NOT_EXISTS = {
    "status": falcon.HTTP_404,
    "title": "User Not Exists",
}

class AppError(Exception):
    def __init__(self, error=BASE_ERROR, description=None):
        self.error = error
        self.error["description"] = description

    @property
    def status(self):
        return self.error["status"]

    @property
    def title(self):
        return self.error["title"]
    
    @property
    def description(self):
        return self.error["description"]

    @staticmethod
    def error_handler(exception, req, resp, error=None):
        resp.status = exception.status
        data = {}
        data["message"] = exception.title
        if exception.description:
            data["description"] = exception.description
        resp.body = json.dumps({"response": data })
    

class MethodNotSupportedError(AppError):
    def __init__(self, method, url):
        super().__init__(METHOD_NOT_SUPPORTED)
        if method and url:
            self.error["description"] = f"Method {method} on {url} not supported"

class UserDoesNotExistError(AppError):
    def __init__(self, user_id):
        super().__init__(USER_DOES_NOT_EXIST)
        self.error["description"] = f"User with id {user_id} not found"

class WrongPassword(AppError):
    def __init__(self):
        super().__init__(PASSWORD_MISMATCH)
        self.error["description"] = "Password doesnot match"

class UserNotExistsError(AppError):
    def __init__(self, description=None):
        super().__init__(ERR_USER_NOT_EXISTS)
        self.error["description"] = description