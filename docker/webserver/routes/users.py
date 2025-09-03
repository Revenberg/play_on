from flask import Blueprint, render_template_string, request
from db import get_db_connection, generate_token, sha256

users_bp = Blueprint('users', __name__)

@users_bp.route('/users', methods=['GET', 'POST'])
def users():
    conn = get_db_connection()
    msg = ""
    with conn.cursor() as cur:
        cur.execute("SELECT id, name FROM teams")
        teams = cur.fetchall()
    if request.method == 'POST':
        username = request.form.get('username')
        team_id = request.form.get('team_id')
        token = generate_token()
        password_hash = sha256(request.form.get('password'))
        if username and team_id and token and password_hash:
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
                    exists = cur.fetchone()[0]
                    if exists:
                        msg = f"Error: Username '{username}' already exists."
                    else:
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
        <input type="text" name="password" placeholder="Password" required>
        <input type="submit" value="Add User">
    </form>
    <p style="color:green;">{{msg}}</p>
    <table border=1>
        <tr><th>ID</th><th>Username</th><th>Team ID</th><th>Token</th><th>Password Hash</th><th>Last Update</th></tr>
        {% for row in rows %}
        <tr><td>{{row[0]}}</td><td>{{row[1]}}</td><td>{{row[2]}}</td><td>{{row[3]}}</td><td>{{row[4]}}</td><td>{{row[5]}}</td></tr>
        {% endfor %}
    </table>
    <a href='/'>Back</a>
    """, rows=rows, teams=teams, msg=msg)
