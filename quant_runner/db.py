import sqlite3

DB_PATH = r"D:\Github\openalgo\db\openalgo.db"

def db_connect():
    return sqlite3.connect(DB_PATH, timeout=30)
