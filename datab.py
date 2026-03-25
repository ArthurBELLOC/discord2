import psycopg

def get_conn():
    return psycopg.connect(
        host="localhost",
        dbname="discord2",
        user="postgres",      
        password="root",
        port=5432             
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

def create_channel(name, password):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO channels (name, password) VALUES (%s,%s) RETURNING id;",
                (name,password),
            )
            chann_id = cur.fetchone()[0]
    return chann_id

def get_channel_by_name(name):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, password FROM channels WHERE name = %s;",
                (name,),
            )
            return cur.fetchone()

def get_channel_by_credentials(name, password):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, password FROM channels WHERE name = %s AND password = %s;",
                (name, password),
            )
            return cur.fetchone()
        
def save_message(channel_id, user_id, content) : 
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO messages(channel_id,user_id,content) VALUES (%s,%s,%s);",
                (channel_id, user_id, content),
            )

def get_histo(channel_id) : 
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT u.username, m.content, m.created_at FROM messages m JOIN users u ON m.user_id = u.id WHERE m.channel_id = %s ORDER BY m.created_at DESC;",
                (channel_id,)
            )
            rows = cur.fetchall()
    return rows[::-1]