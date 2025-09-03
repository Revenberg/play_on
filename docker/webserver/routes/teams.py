from flask import Blueprint, render_template_string, request
from db import get_db_connection

teams_bp = Blueprint('teams', __name__)

@teams_bp.route('/teams', methods=['GET', 'POST'])
def teams():
    conn = get_db_connection()
    msg = ""
    if request.method == 'POST':
        team_name = request.form.get('team_name')
        if team_name:
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT COUNT(*) FROM teams WHERE teamname = %s", (team_name,))
                    exists = cur.fetchone()[0]
                    if exists:
                        msg = f"Error: Team name '{team_name}' already exists."
                    else:
                        cur.execute("INSERT INTO teams (teamname) VALUES (%s)", (team_name,))
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
