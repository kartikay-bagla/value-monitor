import datetime as dt
import sqlite3
import psutil
import requests
from value_logger.utils import getenv
from apscheduler.schedulers.blocking import BlockingScheduler

SECRET_KEY = getenv("SECRET_KEY")
DEVICE_NAME = getenv("DEVICE_NAME")
DB_FILE_NAME = getenv("DB_FILE_NAME")
API_URL = getenv("API_URL")


def _init_table(db):
    cursor = db.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS metrics (time TEXT, cpu REAL, ram REAL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS last_executed (time TEXT)")


def add_entry_to_db():
    db = sqlite3.connect(DB_FILE_NAME)
    now = dt.datetime.now()
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    print(f"Adding to DB: {now} {cpu} {ram}")
    cursor = db.cursor()
    cursor.execute("INSERT INTO metrics VALUES (?, ?, ?)", (now, cpu, ram))
    db.commit()


def update_api():
    db = sqlite3.connect(DB_FILE_NAME)
    cursor = db.cursor()
    # get last updated
    cursor.execute("SELECT time FROM last_executed limit 1")
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
    print(f"Pushing {len(metrics)} to API")
    # push to API
    resp = requests.post(API_URL, json=metrics, headers={"secret-key": SECRET_KEY})
    if resp.status_code != 200:
        print(f"Update API failed with code {resp.status_code}.")
        print(resp.json())
        return
    # update last updated
    print("Updating last executed.")
    cursor.execute("UPDATE last_executed SET time = ?", (dt.datetime.now(),))
    db.commit()


db = sqlite3.connect(DB_FILE_NAME)
_init_table(db=db)
db.close()

bs = BlockingScheduler()
bs.add_job(add_entry_to_db, 'interval', seconds=5)
bs.add_job(update_api, 'interval', minutes=1)
bs.start()
