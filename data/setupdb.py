import os
import sqlite3

def main():
    exchanges = ['gdax','gemini']

    for exchange in exchanges:
        db = "trade-" + exchange  +".db"
        if not os.path.exists(db):
            conn = sqlite3.connect(db)
            cur = conn.cursor()
            cur.execute('''CREATE TABLE orders (ID INTEGER PRIMARY KEY AUTOINCREMENT, DATE TEXT NOT NULL, TYPE INTEGER NOT NULL, SYM TEXT NOT NULL, QTY REAL NOT NULL, BID REAL NOT NULL, STATUS TEXT NOT NULL, DESCRIPTION TEXT)''')
            conn.commit()
            conn.close()
            print ("Created database: %s" % db)
        else:
            print ("Found existing database file %s, no action taken." % db)

        db = "ticker-" + exchange  +".db"
        if not os.path.exists(db):
            conn = sqlite3.connect(db)
            cur = conn.cursor()
            conn.execute('''CREATE TABLE ticker (DATE TEXT PRIMARY KEY, SYM TEXT NOT NULL, VALUE REAL NOT NULL)''')
            conn.commit()
            conn.close()
            print ("Created database: %s" % db)
        else:
            print ("Found existing database file %s, no action taken." % db)

if __name__ == "__main__":
    main()
