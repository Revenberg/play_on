import pymysql
import os

def get_db_connection():
    return pymysql.connect(
        host=os.environ.get('DB_HOST', 'mysql'),
        user=os.environ.get('DB_USER', 'admin'),
        password=os.environ.get('DB_PASSWORD', 'admin'),
        database=os.environ.get('DB_NAME', 'gameon'),
        autocommit=True
    )

def create_tables(conn):
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(64) UNIQUE,
            team_id INT,
            token VARCHAR(128),
            password_hash VARCHAR(128)
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
            snr FLOAT
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

def process_lora_message(msg, conn):
    # TODO: Parse and split msg into tables
    # Example stub: print(msg)
    print(f"Received LoRa message: {msg}")
    # Implement parsing and DB insertion logic here

def main():
    conn = get_db_connection()
    create_tables(conn)
    # TODO: Replace with actual LoRa message reading logic
    # For now, simulate receiving a message
    test_msg = "node1;user1;teamA;object;function;parameters;2025-09-01 12:00:00"
    process_lora_message(test_msg, conn)

if __name__ == "__main__":
    main()
