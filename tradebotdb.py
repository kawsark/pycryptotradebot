import sqlite3
import datetime
from sqlite3 import Error

class Tradebotdb:

    def preporder(self,sym,qty,bid):
        cursor = self.conn.cursor()
        t = datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S.%f")
        c1 = cursor.execute("insert into orders (DATE, TYPE, SYM, QTY, BID, STATUS) values (?,?,?,?,?,?)", (t,0,sym,qty,bid,"pending") )
        self.conn.commit()
        return int(c1.lastrowid)

    def updateorder(self,id,status, description):
        cursor = self.conn.cursor()
        c1 = cursor.execute("update orders set status = ?, description = ? where id = ?", (status, description, id) )
        self.conn.commit()

    def getorderstatus(self,id):
        cursor = self.conn.cursor()
        c1 = cursor.execute("SELECT STATUS FROM orders WHERE id=?", (id,) )
        return c1.fetchone()[0]

    def printorder(self,id):
        cursor = self.conn.cursor()
        print("printing order id %d" % id)
        c1 = cursor.execute("SELECT * FROM orders WHERE id=?", (id,) )
        print(c1.fetchone())


    def gracefulstop(self):
        if self.conn is not None:
            self.conn.close()

    def __init__(self,exchange):
        self.conn = None
        db_file = "data/trade-"+exchange+".db"
        try:
            self.conn = sqlite3.connect(db_file)

        except Error as e:
            print(e)
