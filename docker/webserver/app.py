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

@app.route('/users', methods=['GET', 'POST'])
def users():
        conn = get_db_connection()
        msg = ""
        # Get available teams for dropdown
        with conn.cursor() as cur:
                cur.execute("SELECT id, name FROM teams")
                teams = cur.fetchall()
        if request.method == 'POST':
                username = request.form.get('username')
                team_id = request.form.get('team_id')
                token = request.form.get('token')
                password_hash = request.form.get('password_hash')
                if username and team_id and token and password_hash:
                        try:
                                with conn.cursor() as cur:
                                        cur.execute("INSERT INTO users (username, team_id, token, password_hash) VALUES (%s, %s, %s, %s)",
                                                                (username, team_id, token, password_hash))
                                msg = f"User '{username}' added successfully."
                        except Exception as e:
                                msg = f"Error adding user: {e}"
        with conn.cursor() as cur:
                cur.execute("SELECT * FROM users")
                rows = cur.fetchall()
        return render_template_string("""
        <h2>Users</h2>
        <form method="post">
            <input type="text" name="username" placeholder="Username" required>
            <select name="team_id" required>
                <option value="">Select Team</option>
                {% for team in teams %}
                <option value="{{team[0]}}">{{team[1]}}</option>
                {% endfor %}
            </select>
            <input type="text" name="token" placeholder="Token" required>
            <input type="text" name="password_hash" placeholder="Password Hash" required>
            <input type="submit" value="Add User">
        </form>
        <p style="color:green;">{{msg}}</p>
        <table border=1>
            <tr><th>ID</th><th>Username</th><th>Team ID</th><th>Token</th><th>Password Hash</th></tr>
            {% for row in rows %}
            <tr><td>{{row[0]}}</td><td>{{row[1]}}</td><td>{{row[2]}}</td><td>{{row[3]}}</td><td>{{row[4]}}</td></tr>
            {% endfor %}
        </table>
        <a href='/'>Back</a>
        """, rows=rows, teams=teams, msg=msg)

@app.route('/teams', methods=['GET', 'POST'])
def teams():
    conn = get_db_connection()
    msg = ""
    if request.method == 'POST':
        team_name = request.form.get('team_name')
        if team_name:
            try:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO teams (name) VALUES (%s)", (team_name,))
                msg = f"Team '{team_name}' added successfully."
            except Exception as e:
                msg = f"Error adding team: {e}"
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM teams")
        rows = cur.fetchall()
    return render_template_string("""
    <h2>Teams</h2>
    <form method="post">
      <input type="text" name="team_name" placeholder="New team name" required>
      <input type="submit" value="Add Team">
    </form>
    <p style="color:green;">{{msg}}</p>
    <table border=1>
      <tr><th>ID</th><th>Name</th></tr>
      {% for row in rows %}
      <tr><td>{{row[0]}}</td><td>{{row[1]}}</td></tr>
      {% endfor %}
    </table>
    <a href='/'>Back</a>
    """, rows=rows, msg=msg)

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
