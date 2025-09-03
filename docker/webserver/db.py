import pymysql, os, secrets, hashlib

def get_db_connection():
    return pymysql.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        user=os.environ.get('DB_USER', 'mysqladmin'),
        password=os.environ.get('DB_PASSWORD', 'adminpassword'),
        database=os.environ.get('DB_NAME', 'gameon'),
        autocommit=True
    )

def sha256(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token(length=32):
    return secrets.token_hex(length // 2)
