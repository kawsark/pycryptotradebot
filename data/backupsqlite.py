#! /usr/bin/env python
# https://gist.github.com/achimnol/3021995
# Of course, the author does not guarantee safety.
# I did my best by using SQLite's online backup API.
from __future__ import print_function
import sys, ctypes
from ctypes.util import find_library
import argparse
import sqlite3
import datetime

SQLITE_OK = 0
SQLITE_ERROR = 1
SQLITE_BUSY = 5
SQLITE_LOCKED = 6

SQLITE_OPEN_READONLY = 1
SQLITE_OPEN_READWRITE = 2
SQLITE_OPEN_CREATE = 4

sqlite = ctypes.CDLL(find_library('sqlite3'))
sqlite.sqlite3_backup_init.restype = ctypes.c_void_p


def removeoldentries(db,table,daysold):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    t = datetime.datetime.now()
    td = datetime.timedelta(days=daysold)
    t1 = t - td
    t1str = t1.strftime("%y-%m-%d %H:%M:%S.%f")

    c1 = cursor.execute("select count(SYM) from " + table + " WHERE DATE < ?", (t1str,))
    rows = c1.fetchone()
    cursor.execute("delete from " + table + " WHERE DATE < ?", (t1str,))
    
    print("Deleted all records before %d days, rows deleted: %s" % (daysold,rows[0]))
    conn.commit()
    conn.close()

def performbackup(source_db,destination_db):
    p_src_db = ctypes.c_void_p(None)
    p_dst_db = ctypes.c_void_p(None)
    null_ptr = ctypes.c_void_p(None)

    ret = sqlite.sqlite3_open_v2(source_db, ctypes.byref(p_src_db), SQLITE_OPEN_READONLY, null_ptr)
    assert ret == SQLITE_OK
    assert p_src_db.value is not None
    ret = sqlite.sqlite3_open_v2(destination_db, ctypes.byref(p_dst_db), SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE, null_ptr)
    assert ret == SQLITE_OK
    assert p_dst_db.value is not None

    print('starting backup...')
    p_backup = sqlite.sqlite3_backup_init(p_dst_db, 'main', p_src_db, 'main')
    print('  backup handler: {0:#08x}'.format(p_backup))
    assert p_backup is not None

    while True:
        ret = sqlite.sqlite3_backup_step(p_backup, 20)
        remaining = sqlite.sqlite3_backup_remaining(p_backup)
        pagecount = sqlite.sqlite3_backup_pagecount(p_backup)
        print('  backup in progress: {0:.2f}%'.format((pagecount - remaining) / float(pagecount) * 100))
        if remaining == 0:
            break
        if ret in (SQLITE_OK, SQLITE_BUSY, SQLITE_LOCKED):
            sqlite.sqlite3_sleep(100)

    sqlite.sqlite3_backup_finish(p_backup)

    sqlite.sqlite3_close(p_dst_db)
    sqlite.sqlite3_close(p_src_db)
    
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Backup a single SQLite3 Database and optionally delete old entries.')
    parser.add_argument('source_db', metavar='src_db', help='File name for source Database')
    parser.add_argument('--table', metavar='table', help='Optional parameter for table name to delete old entries from')
    parser.add_argument('destination_db', metavar='dest_db', help='File name for destination Database')
    parser.add_argument('--rmolderthan', metavar='N', type=int, help='Delete entries older than this # of days. Should be > 0 days or no action taken')


    args = parser.parse_args()

    #Call backup function
    performbackup(args.source_db,args.destination_db)
    
    #Call remove old entries
    if args.rmolderthan is not None and args.rmolderthan > 0:
        removeoldentries(args.source_db,args.table,args.rmolderthan)

