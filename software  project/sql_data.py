import mysql.connector as msc

conn = msc.connect(host = '127.0.0.1',port = 3306,user='root',password='Dhanu@2003',database = 'software')

cur = conn.cursor()

cur.execute('select * from login')