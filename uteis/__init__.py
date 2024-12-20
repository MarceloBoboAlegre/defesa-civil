import mysql.connector


def conectar_bd():
    database = mysql.connector.connect(
        host='jsk3f4rbvp8ayd7w.cbetxkdyhwsb.us-east-1.rds.amazonaws.com',
        user='wo5cnrmp0qtloa87',
        password='e6kxjigelgpg39vs',
        database='amvc1vx3l9sfjbux'
    )
    return database


def cursor_on(database):
    mycursor = database.cursor()
    return mycursor


def turnoff(cursor, database):
    cursor.close()
    database.close()


def get_markers():
    db = conectar_bd()
    myc = cursor_on(db)

    sql = "SELECT id_chamado, data_chamado, latitude, longitude, situacao, tipo_ocorrencia FROM chamados"
    myc.execute(sql)
    markers = myc.fetchall()

    turnoff(myc, db)

    lista = list(markers)
    return lista


def gerador_pdf(id):
    db = conectar_bd()
    myc = db.cursor(dictionary=True)

    sql = "SELECT * FROM chamados WHERE id_chamado = %s"
    val = (id, )
    myc.execute(sql, val)
    cadastro = myc.fetchone()
    id_cad = cadastro['id_chamado']

    sql = "SELECT caminho FROM imagens WHERE cadastro_id = %s"
    val = (id_cad, )
    myc.execute(sql, val)
    imagens = myc.fetchall()
    turnoff(myc, db)
    info = [cadastro, imagens]
    return info


def cadastro(data, origem, nome, documento, telefone1, telefone2, email, 
            logradouro, numero, bairro, complemento, ponto_referencia, 
            latitude, longitude, ocorrencia, tipo_ocorrencia, situacao, area, pmrr, imagens):
    db = conectar_bd()
    myc = cursor_on(db)
    
    # Inserindo informações no Banco de dados
    sql = ('INSERT INTO chamados (data_chamado, origem_chamado, nome, documento, telefone1, telefone2, email, logradouro, numero, bairro, complemento, ponto_referencia, latitude, longitude, ocorrencia, tipo_ocorrencia, situacao, area, pmrr) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)')
    val = (data, origem, nome.capitalize(), documento, telefone1, telefone2, email, 
        logradouro, numero, bairro, complemento, ponto_referencia, 
        latitude, longitude, ocorrencia, tipo_ocorrencia, situacao, area, pmrr.upper())
    try:
        myc.execute(sql, val)
    except Exception:
        turnoff(myc, db)
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
