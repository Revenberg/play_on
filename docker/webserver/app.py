from flask import Flask, render_template_string, request, redirect, url_for
import pymysql
import os

app = Flask(__name__)

def get_db_connection():
    return pymysql.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        user=os.environ.get('DB_USER', 'mysqladmin'),
        password=os.environ.get('DB_PASSWORD', 'adminpassword'),
        database=os.environ.get('DB_NAME', 'gameon'),
        autocommit=True
    )

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

@app.route('/users')
def users():
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM users")
        rows = cur.fetchall()
    return render_template_string("""
    <h2>Users</h2>
    <table border=1>
      <tr><th>ID</th><th>Username</th><th>Team ID</th><th>Token</th><th>Password Hash</th></tr>
      {% for row in rows %}
      <tr><td>{{row[0]}}</td><td>{{row[1]}}</td><td>{{row[2]}}</td><td>{{row[3]}}</td><td>{{row[4]}}</td></tr>
      {% endfor %}
    </table>
    <a href='/'>Back</a>
    """, rows=rows)

@app.route('/teams')
def teams():
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM teams")
        rows = cur.fetchall()
    return render_template_string("""
    <h2>Teams</h2>
    <table border=1>
      <tr><th>ID</th><th>Name</th></tr>
      {% for row in rows %}
      <tr><td>{{row[0]}}</td><td>{{row[1]}}</td></tr>
      {% endfor %}
    </table>
    <a href='/'>Back</a>
    """, rows=rows)

@app.route('/lora_nodes')
def lora_nodes():
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM lora_nodes")
        rows = cur.fetchall()
    return render_template_string("""
    <h2>LoRa Nodes</h2>
    <table border=1>
      <tr><th>ID</th><th>Node ID</th><th>Last Seen</th><th>RSSI</th><th>SNR</th></tr>
      {% for row in rows %}
      <tr><td>{{row[0]}}</td><td>{{row[1]}}</td><td>{{row[2]}}</td><td>{{row[3]}}</td><td>{{row[4]}}</td></tr>
      {% endfor %}
    </table>
    <a href='/'>Back</a>
    """, rows=rows)

@app.route('/messages')
def messages():
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM messages")
        rows = cur.fetchall()
    return render_template_string("""
    <h2>Messages</h2>
    <table border=1>
      <tr><th>ID</th><th>Node ID</th><th>User ID</th><th>Team ID</th><th>Object</th><th>Function</th><th>Parameters</th><th>Timestamp</th></tr>
      {% for row in rows %}
      <tr><td>{{row[0]}}</td><td>{{row[1]}}</td><td>{{row[2]}}</td><td>{{row[3]}}</td><td>{{row[4]}}</td><td>{{row[5]}}</td><td>{{row[6]}}</td><td>{{row[7]}}</td></tr>
      {% endfor %}
    </table>
    <a href='/'>Back</a>
    """, rows=rows)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
