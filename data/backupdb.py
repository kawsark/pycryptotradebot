import backupsqlite
import time

def main():
    exchanges = ['gdax','gemini']

    #Backup trade dbs
    for exchange in exchanges:
        src_db = "trade-" + exchange  +".db"
        dest_db = src_db + "-backup." + str(time.time()).split('.')[0]
        backupsqlite.performbackup(src_db,dest_db)
        backupsqlite.removeoldentries(src_db,"orders",60)

    #Backup ticker dbs
    for exchange in exchanges:
        src_db = "ticker-" + exchange  +".db"
        dest_db = src_db + "-backup." + str(time.time()).split('.')[0]
        backupsqlite.performbackup(src_db,dest_db)
        backupsqlite.removeoldentries(src_db,"ticker",60)

if __name__ == '__main__':
    main()

