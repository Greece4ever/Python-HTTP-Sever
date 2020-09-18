"""
Use a simple sqlite3 db for simply caching things
"""
import sqlite3
import time
from typing import Tuple

class Cache:
    def __init__(self,filename : str,req_rate : Tuple[int,str]):
        self.connection = sqlite3.connect(filename)
        self.cursor = self.connection.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS CACHE (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip text,
                last_check integer,
                checks integer
            )
        """)
        self.connection.commit()
        self.requests = req_rate #  (10/'y') , (10/'m') , (10/'d'), (10/'h') , (10/'m') , (10/'s') 

    def save(self,ip):
        isCached = self.check(ip).fetchall()
        if not len(isCached) == 0:
            self.cursor.execute("""
            UPDATE CACHE
            SET last_check = ?, checks = ?
            WHERE ip = ?
            """,(time.time(),isCached[0][-1] + 1,ip))
        else:
            self.cursor.execute("""
                INSERT INTO CACHE VALUES (null,?,?,?)
            """,(ip,time.time(),1))
        return self.connection.commit()

    def check(self,ip):
        query = self.cursor.execute("""
            SELECT * FROM CACHE
            WHERE ip = ?
        """,(ip,))
        return query

    def isBlock(self):
        pass


cache = Cache("cache.sqlite3")
# cache.save("17.321312.321")
x = cache.save("192.168.1.1")
x = cache.check("192.168.1.1")
print(x.fetchall())