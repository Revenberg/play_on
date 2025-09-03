from flask import Blueprint, render_template_string, request
from db import get_db_connection

lora_nodes_bp = Blueprint('lora_nodes', __name__)

@lora_nodes_bp.route('/lora_nodes')
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
