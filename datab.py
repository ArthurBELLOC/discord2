import psycopg

def get_conn():
    return psycopg.connect(
        host="localhost",
        dbname="fih",
        user="postgres",      # ou ton user si tu en as créé un autre
        password="root",
        port=8765             # le port que tu as mis dans le shell
    )
def create_user(username, password):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s) RETURNING id;",
                (username, password),
            )
            user_id = cur.fetchone()[0]
    return user_id

def get_user_by_credentials(username, password):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM users WHERE username = %s AND password = %s;",
                (username, password),
            )
            row = cur.fetchone()
    if row is None:
        return None
    return row[0]