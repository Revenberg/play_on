from flask import Flask, render_template_string, request, redirect, url_for
import pymysql
import os
import hashlib
import secrets
from routes.users import users_bp
from routes.teams import teams_bp
from routes.lora_nodes import lora_nodes_bp
from routes.messages import messages_bp

app = Flask(__name__)
app.register_blueprint(users_bp)
app.register_blueprint(teams_bp)
app.register_blueprint(lora_nodes_bp)
app.register_blueprint(messages_bp)

def get_db_connection():
    return pymysql.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        user=os.environ.get('DB_USER', 'mysqladmin'),
        password=os.environ.get('DB_PASSWORD', 'adminpassword'),
        database=os.environ.get('DB_NAME', 'gameon'),
        autocommit=True
    )

def sha256(password):
    hash_hex = hashlib.sha256(password.encode()).hexdigest()
    return hash_hex

def generate_token(length=32):
    """
    Generates a secure random token for user authentication.
    :param length: Length of the token string.
    :return: Hexadecimal token string.
    """
    return secrets.token_hex(length // 2)

@app.route('/')
def index():
    return render_template_string("""
    <h1>GameOn Database Maintenance</h1>
    <ul>
      <li><a href='/users'>Users</a></li>
      <li><a href='/teams'>Teams</a></li>
      <li><a href='/lora_nodes'>LoRa Nodes</a></li>
      <li><a href='/messages'>Messages</a></li>
    </ul>
    """)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
