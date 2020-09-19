"""
For caching Requests and saving them in a small SQLITE3 Local DB\n
Normal CACHE Parameter is the IP of the REQUESTED CLIENT\n
You can create multiple CACHES in one DB or create more than one DB'S\n
"""
import sqlite3
import time
import datetime
from typing import Tuple,Optional

class Cache:
    """
    __init__ : method,\n (filename : 'Filename Where db will be stored',cache_name : 'Name of Database Table',req_rate : 'Request Rate')
        param: filename (Where the sqlite3 file is saved)
        param: req_rate (Optional : Maximum Number of requests made in a specific interval) (Request Number,Datetime Timedelta)
        param: cache_name (Name of the Database Table)
    save : method
    check : method
    handleTime method
        param: ip (The IP the operations are going to be performed in)
    """
    def __init__(self,filename : str,cache_name : str,req_rate : Tuple[int,datetime.timedelta]):
        self.connection = sqlite3.connect(filename)
        self.cachename = cache_name
        self.cursor = self.connection.cursor()
        self.filename = filename
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS {} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip text,
                last_check integer,
                checks integer
            )
        """.format(self.cachename))
        self.connection.commit()
        self.rate = req_rate 

    def save(self,ip,cac_val : Optional[int] = None):
        """Cache the IP at the moment the function is called"""
        isCached = self.check(ip).fetchall()
        if not len(isCached) == 0:
            if cac_val is None:
                cac_val : int = isCached[0][-1] + 1
            self.cursor.execute("""
            UPDATE {}
            SET last_check = ?, checks = ?
            WHERE ip = ?
            """.format(self.cachename),(time.time(),cac_val,ip))
        else:
            self.cursor.execute("""
                INSERT INTO {} VALUES (null,?,?,?)
            """.format(self.cachename),(ip,time.time(),1))
        return self.connection.commit()

    def check(self,ip):
        """Check the cache for values on a specific IP"""
        query = self.cursor.execute("""
            SELECT * FROM {}
            WHERE ip = ?
        """.format(self.cachename),(ip,))
        return query

    def handleTime(self,ip):
        beg_data = self.check(ip).fetchall()[0]
        time_since_last_commit = datetime.datetime.now() - datetime.datetime.fromtimestamp(beg_data[-2]) #timedelta
        if time_since_last_commit < self.rate[1]: #if the time interval since the last request has not passed
            if beg_data[-1] > self.rate[0]:
                print("(CACHE) Blocked request with time difference {} ({})".format(time_since_last_commit,ip))
                return False # Suitable for 429 Status
            return True
        self.save(ip,0) #Set The Connection Attempts to 0
        return True

    def CacheDecorator(self,function : callable):
        """Save into Cache visits at a page"""
        def wrapper(*args,**kwargs):
            self.connection = sqlite3.connect(self.filename)
            self.cursor = self.connection.cursor()
            IP = args[-1]['IP']
            try:
                isPermitted = self.handleTime(IP)
            except Exception as f:
                print(f)
                isPermitted = True
            finally:
                self.save(IP)
                return function(*args,**kwargs,isPermitted=isPermitted)
        return wrapper

if __name__ == "__main__":
    pass