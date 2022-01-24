from random import random
import bcrypt
from datetime import datetime, timedelta
import falcon
import json
import jwt

from app.base import BaseResource
from app.database import execute_query
from app.utils import *


FETCH_ALL_USERS = "SELECT * from users;"
CREATE_USER = "INSERT INTO users (username, password, created_at, updated_at, token, token_expires_in) VALUES('{}', '{}', '{}', '{}', '{}', '{}');"
FETCH_USER = " SELECT * from users WHERE username = '{}';"
UPDATE_TOKEN = "UPDATE users SET token = '{}' , token_expires_in = {} where id = {};"
CHECK_USER_BY_TOKEN = "select * from users where token = '{}';"

class Users(BaseResource):
    """
    Handle for end-point api/v1/users
    """
    def on_get(self, req, resp):
        validate_token(req, resp)
        data = "No users to fetch"
        resp.status = falcon.HTTP_200
        query = FETCH_ALL_USERS
        users = execute_query(query, "Fetching all users")
        print("Users =>", users)
        if users:
            users_data = []
            for user_row in users:
                user = { 
                    "user_id" : user_row[0],
                    "username" :  user_row[1],
                    "created_at" : user_row[3],
                    "updated_at" : user_row[4] }
                users_data.append(user)
            data = users_data
        resp.body = self.to_json({"users": data})


class Register(BaseResource):

    def on_post(self, req, resp):
        data = json.loads(req.stream.read().decode('utf-8'))
        username = data["username"]
        password = bcrypt.hashpw(data["password"].encode("utf-8"), bcrypt.gensalt()).decode('utf-8')
        created_at = datetime.today()
        updated_at = datetime.today()
        random_id = uuid()
        token = encrypt_token(random_id).decode("utf-8")
        token_expires_in = datetime.now() + timedelta(minutes=10)
        query =  CREATE_USER.format(username, password, created_at, updated_at, token, token_expires_in)
        result = execute_query(query, "Registering User")
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
    if len(req.get_header("Authorization")) > 0:
        auth_header= req.get_header("Authorization").split(" ")
        auth_token = auth_header[0]
        print("Auth header", auth_header)
    else:
        raise falcon.HTTPUnauthorized(title = 'Authorization Header missing', description = "Pass Auth token in headers")
    query = CHECK_USER_BY_TOKEN.format(auth_token)
    user = execute_query(query, "Authorization")
    print("User ==>",user)
    if len(user) > 0:
        if user[0][6].replace(tzinfo=None) > datetime.now():
            payload = uuid()
            new_token = jwt.encode(payload, get_secret_key(), "HS256").decode("utf-8")
            token_expires_in = datetime.now() + timedelta(minutes=10)
            query = UPDATE_TOKEN.format(new_token, token_expires_in, user[0][0])
            execute_query(query, "login")
        return user[0]
    else:
        raise falcon.HTTPUnauthorized(title = 'Please login before proceeding', description = "This action requires you to login")
