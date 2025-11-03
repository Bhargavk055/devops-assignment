from flask import Flask
import os
import pymysql

app = Flask(__name__)

DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
DB_NAME = os.environ.get('DB_NAME', '')


def check_db():
    try:
        conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME, connect_timeout=5)
        cur = conn.cursor()
        cur.execute('SELECT 1')
        cur.close()
        conn.close()
        return True
    except Exception as e:
        return str(e)


@app.route('/')
def index():
    """Return simple status showing whether DB connection works."""
    status = check_db()
    if status is True:
        return f"Hello — Flask connected to DB '{DB_NAME}' at '{DB_HOST}'."
    else:
        return (f"Hello — DB connection failed: {status}"), 500


if __name__ == '__main__':
    # Use 0.0.0.0 so container ports are reachable from host
    app.run(host='0.0.0.0', port=5000, debug=True)
