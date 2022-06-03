#database connect 
import pymysql

conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='Pass0714',
        database='test_01'
    )   