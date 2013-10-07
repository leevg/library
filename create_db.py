import sqlite3
import config

conn = sqlite3.connect(config.SQLALCHEMY_DATABASE_FILE_URI)
c = conn.cursor()
file = open('create_author.sql', 'r')
for qry in file:
    c.execute(qry)
    conn.commit()
c.close()
conn.close()