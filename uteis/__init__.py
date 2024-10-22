import mysql.connector


def conectar_bd(h, u, pw, db):
    database = mysql.connector.connect(
        host=h,
        user=u,
        password=pw,
        database=db
    )
    return database


def cursor_on(database):
    mycursor = database.cursor()
    return mycursor


def turnoff(cursor, database):
    cursor.close()
    database.close()


def cadastro(nome, email, latitude, longitude):
    db = conectar_bd('localhost', 'root', '', 'defesa')
    myc = cursor_on(db)

    sql = ('INSERT INTO cadastros (NOME, EMAIL, LATITUDE, LONGITUDE) VALUES (%s, %s, %s, %s)')
    val = (nome, email, latitude, longitude)
    try:
        myc.execute(sql, val)
    except:
        print('Erro')
    else:
        db.commit()
        last_id = myc.lastrowid
        print('Sucesso')
    turnoff(myc, db)
