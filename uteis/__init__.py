import mysql.connector


def conectar_bd():
    database = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='defesa'
    )
    return database


def cursor_on(database):
    mycursor = database.cursor()
    return mycursor


def turnoff(cursor, database):
    cursor.close()
    database.close()


def cadastro(nome, email, latitude, longitude, formato, imagens):
    db = conectar_bd()
    myc = cursor_on(db)

    sql = ('INSERT INTO cadastros (NOME, EMAIL, LATITUDE, LONGITUDE, FORMATO) VALUES (%s, %s, %s, %s, %s)')
    val = (nome, email, latitude, longitude, formato)
    try:
        myc.execute(sql, val)
    except:
        print('Erro')
    else:
        db.commit()
        cadastro_id = myc.lastrowid
    # Processar cada imagem
    for imagem in imagens:
            if imagem.filename == '':
                continue
            sql_imagem = "INSERT INTO imagens (cadastro_id, caminho) VALUES (%s, %s)"
            myc.execute(sql_imagem, (cadastro_id, imagem.filename))
            db.commit()
    turnoff(myc, db)


def get_markers():
    db = conectar_bd()
    myc = cursor_on(db)

    sql = "SELECT nome, email, latitude, longitude, formato FROM cadastros"
    myc.execute(sql)
    markers = myc.fetchall()

    turnoff(myc, db)

    lista = list(markers)
    return lista


def gerador_pdf(nome):
    db = conectar_bd()
    myc = db.cursor(dictionary=True)

    sql = "SELECT * FROM cadastros WHERE nome = %s"
    val = (nome, )
    myc.execute(sql, val)
    cadastro = myc.fetchone()
    id_cad = cadastro[0]

    sql = "SELECT caminho FROM imagens WHERE cadastro_id = %s"
    val = (id_cad, )
    myc.execute(sql, val)
    imagens = myc.fetchall()
    turnoff(myc, db)
    info = [cadastro, imagens]
    return info
