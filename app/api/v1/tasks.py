from random import random
import bcrypt
from datetime import datetime, timedelta
import falcon
import json
import jwt

from app.base import BaseResource
from app.database import execute_query
from app.utils import *
from .users import validate_token

FETCH_ALL_TASKS = "SELECT * from tasks where user_id = '{}';"
CREATE_TASK = "INSERT INTO tasks (name, status, user_id) VALUES('{}', '{}', '{}');"
FETCH_USER = " SELECT * from users WHERE username = '{}';"
UPDATE_TOKEN = "UPDATE users SET token = '{}' , token_expires_in = {} where id = {};"
CHECK_USER_BY_TOKEN = "select * from users where token = '{}';"

class Tasks(BaseResource):
    """
    Handle for end-point api/v1/tasks
    """
    def on_get(self, req, resp):
        validate_token(req, resp)
        resp.status = falcon.HTTP_200
        user_id = 1
        query = FETCH_ALL_TASKS.format(user_id)
        tasks = execute_query(query, "Fetching all tasks")
        print("Tasks =>", tasks)
        if tasks:
            tasks_data = []
            for task in tasks:
                data = { 
                    "name" : task[0],
                    "status" :  task[1]
                }
                tasks_data.append(data)
            data = tasks_data
        else:
            data = "No Tasks to display"
        resp.body = self.to_json({"tasks": data})

class TaskAction(BaseResource):
    def on_put(self, req, resp, task_id):
        return super().on_put(req, resp)
    
    def on_delete(self, req, resp, task_id):
        return super().on_delete(req, resp)


class CreateTask(BaseResource):
    def on_post(self, req, resp):
        data = json.loads(req.stream.read().decode('utf-8'))
        user = validate_token(req, resp)
        resp.status = falcon.HTTP_200
        user_id = user[0]
        name = data["name"]
        status = False
        query =  CREATE_TASK.format(name, status, user_id)
        result = execute_query(query, "Create_tasks")
        print(result)
        resp.body = self.to_json(result)


class Login(BaseResource):

    def on_post(self, req, resp):
        data = json.loads(req.stream.read().decode('utf-8'))
        username = data["username"]
        password = data["password"]

        try:
            query = FETCH_USER.format(username)
            result = execute_query(query, "Creating user")
            if len(result) > 0:
                password_from_db = result[0][2].encode("utf-8")
                # entered_pass_hash = bcrypt.hashpw(password)
                # pass_from_db_hash = bcrypt.hashpw(password_from_db)
                # if bcrypt.checkpw(entered_pass_hash, pass_from_db_hash):
                if bcrypt.hashpw(password.encode("utf-8"), password_from_db) == password_from_db:
                    token = result[0][5]
                    resp.body = self.to_json({"token": token})
                else:
                    pass
        except:
            resp.body = self.to_json("Invalid Credentials, Please try again")


def validate_token(req, resp):
    auth_header= req.get_header("Authorization").split(" ")
    if len(auth_header) > 0:
        auth_token = auth_header[0]
    else:
        raise falcon.HTTPUnauthorized(title = 'Authorization Header missing', description = "Pass Auth token in headers")
    query = CHECK_USER_BY_TOKEN.format(auth_token)
    user = execute_query(query, "Authorization")
    if len(user) > 0:
        print(user[0][6].replace(tzinfo=None), datetime.now())
        if user[0][6].replace(tzinfo=None) > datetime.now():
            payload = uuid()
            new_token = jwt.encode(payload, get_secret_key(), "HS256").decode("utf-8")
            token_expires_in = datetime.now() + timedelta(minutes=10)
            query = UPDATE_TOKEN.format(new_token, token_expires_in, user[0][0])
            execute_query(query, "login")
    else:
        raise falcon.HTTPUnauthorized(title = 'Please login before proceeding', description = "This action requires you to login")
