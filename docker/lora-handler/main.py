from tokenize import String
from attr import fields
import pymysql
import os
import time
import serial
import threading

rpibeaconid = None

def get_db_connection(retries=10, delay=3):
    for attempt in range(retries):
        try:
            return pymysql.connect(
                host=os.environ.get('DB_HOST', 'mysql'),
                user=os.environ.get('DB_USER', 'admin'),
                password=os.environ.get('DB_PASSWORD', 'admin'),
                database=os.environ.get('DB_NAME', 'gameon'),
                autocommit=True
            )
        except pymysql.err.OperationalError as e:
            print(f"MySQL connection failed (attempt {attempt+1}/{retries}): {e}")
            time.sleep(delay)
    raise Exception("Could not connect to MySQL after several attempts.")

def create_tables(conn):
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(64) UNIQUE,
            team_id INT,
            token VARCHAR(128),
            password_hash VARCHAR(225),
            last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(64) UNIQUE
        )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS lora_nodes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            node_id VARCHAR(64) UNIQUE,
            last_seen DATETIME,
            rssi FLOAT,
            snr FLOAT,
            version VARCHAR(64)
        )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            node_id VARCHAR(64),
            user_id INT,
            team_id INT,
            object VARCHAR(64),
            `function` VARCHAR(64),
            parameters TEXT,
            timestamp DATETIME
        )
        """)

def parse_fields(msg):
    fields = {}
    for part in msg.split(','):
        if ':' in part:
            key, value = part.split(':', 1)
            fields[key.strip()] = value.strip()
    return fields

def process_lora_message(msg, conn):
    global rpibeaconid
    # Parse message: node_id;user_id;team_id;object;function;parameters;timestamp
    print(f"Received LoRa message: {msg}")

    if msg.startswith("[LoRa RX]") or msg.startswith("[LoRa TX]"):
        if (msg.startswith("[LoRa RX]")) :
            msg = msg[len("[LoRa RX]"):].strip()
        else:
            msg = msg[len("[LoRa TX]"):].strip()
            if (rpibeaconid is None):
                rpibeaconid = "rpi"           
        
        print(f"Received LoRa message: {msg}")

        if msg.startswith('BEACON'):
            msg = msg[len('BEACON;'):].strip()
            fields = parse_fields(msg)
            
            node_id = fields['nodeid']
            rssi = fields['rssi']
            snr = fields['snr']
            nodeversion = fields['version']

            if (rpibeaconid == "rpi"):
                rpibeaconid = node_id
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                    INSERT INTO lora_nodes (node_id, last_seen, rssi, snr, version)
                    VALUES (%s, NOW(), %s, %s, %s)
                    ON DUPLICATE KEY UPDATE last_seen=NOW(), rssi=%s, snr=%s, version=%s
                    """, (node_id, rssi, snr, nodeversion, rssi, snr, nodeversion))
                print("LoRa node info updated in database.")
            except Exception as e:
                print(f"Failed to update LoRa node info: {e}")
            return

        if msg.startswith('test'):
#            msg = msg[len('test'):].strip().strip('"')

            parts = msg.split(';')
            node_id, user_id, team_id, obj, func, params, timestamp = parts
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                    INSERT INTO messages (node_id, user_id, team_id, object, `function`, parameters, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (node_id, user_id, team_id, obj, func, params, timestamp))
                print("Message inserted into database.")
            except Exception as e:
                print(f"Failed to insert message: {e}")

def loraSend(ser, nodeMessage):
    # Send the LoRa message
    print(f"Sending LoRa message: {nodeMessage}")
    msgID = millis()
    msg = "MSG;" + String(msgID) + ";RPI;" + 3 + ";" + nodeMessage
    ser.write((msg + "\n").encode('utf-8'))

def check_user_updates(ser, conn):
    import datetime
    last_user_update = datetime.datetime(2025, 1, 1)
    while True:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE last_update > %s", (last_user_update,))
            rows = cur.fetchall()
            for row in rows:
                print(f"User update found: {row}")
                last_user_update = row['last_update']

                username = row['Username']
                pwdHash = row['password_hash']
                token = row['token']
                team = row['team']

                loraSend(ser, "USER;ADD; name:" + username + ",pwdHash:" + pwdHash + ",token:" + token + ",team:" + team)
                time.sleep(5)  # Wait 10 seconds

        time.sleep(60)  # Wait 60 seconds

def main():
    print(f"main")
    conn = get_db_connection()
    print(f"connection established")
    create_tables(conn)
    print(f"Tables created")
    usb_port = os.environ.get('USB_PORT', '/dev/ttyUSB0')
    baudrate = int(os.environ.get('USB_BAUDRATE', '115200'))
    print(f"Using USB port: {usb_port} at baudrate: {baudrate}")
    connection = False
    ser = None
    while not connection:
        try:
            ser = serial.Serial(usb_port, baudrate, timeout=1)
            print(f"Listening for LoRa messages on {usb_port}...")
            connection = True
        except Exception as e:
            print(f"Failed to open USB port: {e}")

    # Start the background thread for checking user updates
    threading.Thread(target=check_user_updates, args=(ser, conn), daemon=True).start()

    while True:
        line = ser.readline().decode('utf-8').strip()
        if line:
            print(f"Received LoRa message: {line}")
            try:
                process_lora_message(line, conn)
            except Exception as e:
                print(f"Error processing LoRa message: {e}")

if __name__ == "__main__":
    main()
