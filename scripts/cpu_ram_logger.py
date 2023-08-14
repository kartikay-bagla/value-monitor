import datetime as dt
import sqlite3
import psutil
import requests
from value_logger.utils import every, getenv

SECRET_KEY = getenv("SECRET_KEY")
DEVICE_NAME = getenv("DEVICE_NAME")
DB_FILE_NAME = getenv("DB_FILE_NAME")
API_URL = getenv("API_URL")

db = sqlite3.connect(DB_FILE_NAME)


def _init_table(db):
    cursor = db.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS metrics (time TEXT, cpu REAL, ram REAL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS last_executed (time TEXT)")


def add_entry_to_db(db):
    now = dt.datetime.now()
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    cursor = db.cursor()
    cursor.execute("INSERT INTO metrics VALUES (?, ?, ?)", (now, cpu, ram))
    db.commit()


def update_api(db):
    cursor = db.cursor()
    # get last updated
    cursor.execute("SELECT last_executed FROM last_executed limit 1")
    result = cursor.fetchone()
    if result is None:
        last_updated = dt.datetime.now()
        cursor.execute("INSERT INTO last_executed VALUES (?)", (last_updated,))
        db.commit()
    else:
        last_updated = dt.datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S.%f")
    # get all entries since last_updated to now
    cursor.execute("SELECT * FROM metrics WHERE time > ?", (last_updated,))
    result = cursor.fetchall()
    metrics = []
    for row in result:
        metrics.append(
            {
                "device_name": DEVICE_NAME,
                "metric_name": "cpu",
                "metric_value": row[1],
                "timestamp": row[0],
            }
        )
        metrics.append(
            {
                "device_name": DEVICE_NAME,
                "metric_name": "ram",
                "metric_value": row[2],
                "timestamp": row[0],
            }
        )
    # push to API
    resp = requests.post(API_URL, json=metrics, headers={"secret-key": SECRET_KEY})
    if resp.status_code != 200:
        print(f"Update API failed with code {resp.status_code}.")
        print(resp.json())
        return
    # update last updated
    cursor.execute("UPDATE last_executed SET last_executed = ?", (dt.datetime.now(),))
    db.commit()


_init_table(db=db)
every(5, add_entry_to_db, db=db)
every(60, update_api, db=db)
