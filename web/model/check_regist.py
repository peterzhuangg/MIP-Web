from model.config import conn

cur = conn.cursor()

def add_user(username, password):
    # sql commands
    sql = "INSERT INTO user(username, password) VALUES ('%s','%s')" %(username, password)
    # execute(sql)
    cur.execute(sql)
    # commit
    conn.commit()  # commit for change of database
    conn.close()