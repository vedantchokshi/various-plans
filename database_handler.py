import sqlite3

dbName = 'vplans_db.db'


def reset():
    conn = sqlite3.connect(dbName)
    print("Opened database successfully")

    conn.execute('CREATE TABLE Plans (id INT PRIMARY KEY, name TEXT)')
    print("Table created successfully")
    conn.close()


# takes a form and returs the new plan's id
def create_plan(form):
    try:
        name = form['name']

        # TODO Remove catches and finally, with statement does this already
        with sqlite3.connect(dbName) as con:
            cur = con.cursor()
            cur.execute("INSERT INTO Plans (name) VALUES (?)", (name))

            con.commit()
            msg = "Record successfully added"
    except:
        con.rollback()
        msg = "error in insert operation"

    finally:
        con.close()
        return 1
