from flask import Blueprint, render_template_string, request
from db import get_db_connection

messages_bp = Blueprint('messages', __name__)

@messages_bp.route('/messages')
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
