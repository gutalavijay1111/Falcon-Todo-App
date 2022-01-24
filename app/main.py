import falcon
from .base import BaseResource
from .errors import AppError
from app.api.v1 import users, tasks
from .database import initialize_db

class App(falcon.API):
    def __init__(self, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)
        print("API Server is starting")
        initialize_db()
        self.add_route("/", BaseResource())
        self.add_route("/login", users.Login())
        self.add_route("/register", users.Register())
        self.add_route("/v1/users", users.Users())
        self.add_route("/v1/tasks", tasks.Tasks())
        self.add_route("/v1/tasks/{task_id}", tasks.TaskAction())
        self.add_route("/v1/tasks/{task_id}/update", tasks.TaskAction())
        self.add_route("/v1/tasks/{task_id}/delete", tasks.TaskAction())
        self.add_route("/v1/tasks/create", tasks.CreateTask())
        self.add_error_handler(AppError, AppError.error_handler)

        
middleware = []
application = App(middleware=middleware)


if __name__ == "__main__":
    from wsgiref import simple_server

    httpd = simple_server.make_server("127.0.0.1", 5000, application)
    httpd.serve_forever()
