import psycopg2
from urllib.parse import urlparse

def parse():
    result = urlparse("postgres://noteefy_user:noteefy_password@localhost:5432/noteefy")
    username = result.username
    password = result.password
    database = result.path[1:]
    hostname = result.hostname
    port = result.port
    return username, password, database, hostname, port

def create_tables():
    username, password, database, hostname, port = parse()
    conn = psycopg2.connect(database=database, user=username, password=password, host=hostname, port=port)
    cursor = conn.cursor()

    # Create users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password BYTEA NOT NULL
    );
    """)

    # Create todos table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS todos (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        title VARCHAR(50) NOT NULL,
        date DATE,
        tags VARCHAR(255)[],
        description TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == '__main__':
    create_tables()
