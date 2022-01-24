import psycopg2
import falcon

USERS_TABLE = '''create table users (
		id SERIAL PRIMARY KEY, 
		username TEXT NOT NULL, 
		password TEXT NOT NULL, 
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
		token TEXT NULL,
        token_expires_in TIMESTAMPTZ NOT NULL, 
        UNIQUE(username)
	)'''

TASKS_TABLE = """create table tasks (
		id SERIAL PRIMARY KEY,
		name TEXT NOT NULL, 
		status BOOLEAN NOT NULL DEFAULT FALSE, 
        user_id INTEGER NOT NULL
	)"""

def initialize_db():
    execute_query(USERS_TABLE, "Create Users Table")
    execute_query(TASKS_TABLE, "Create Tasks Table")

def execute_query(query, message):
    try:
        conn = psycopg2.connect(database="Falcon", user='postgres',
                        password='123456789', host='127.0.0.1', port= '5432')
        print("Connected to DB")
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute(query)
        if cursor:
            result = []
            for row in cursor:
                result.append(row)
        else:
            result = "User created"
        conn.commit()   
        return result

    except Exception as e:
        print("Internal server error ", e)
        return e

    finally:
        if conn:
            conn.close()
            print("The DB connection is closed")