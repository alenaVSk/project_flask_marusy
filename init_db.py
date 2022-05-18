import sqlite3

connection = sqlite3.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO posts (title, content) VALUES (?, ?)",
            ('First Post', 'Content for the first post')
            )

cur.execute("INSERT INTO posts (title, content) VALUES (?, ?)",
            ('Second Post', 'Content for the second post')
            )

connection.commit()
connection.close()


connection = sqlite3.connect('database.db')

cur = connection.cursor()

cur.execute("INSERT INTO users (name, email, psw, time) VALUES (?, ?, ?, ?)",
            ('lena', 'abc@mail.ru', 'abcd', 123654789)
            )

connection.commit()
connection.close()

