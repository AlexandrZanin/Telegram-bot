import sqlite3 as sq

with sq.connect('histoty.db') as con:
    cur=con.cursor()
    # cur.execute("DROP TABLE IF EXISTS users")
    cur.execute("""CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    addres TEXT NOT NULL,
    distance NOT NULL DEFAULT 1,
    price TEXT,
    stars TEXT)""")
    INSERT INTO users VALUE
    cur.execute('SELECT name, addres, distance, price, stars FROM users WHERE {условие} ORDER BY {сортировать по строке} LIMIT 5 OFSET 2')
    result = cur.fetchall()
    cur.fetchmany(2)#сколько записей