import mysql.connector
import bcrypt



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


def cadastro_user(nome, senha, email, telefone, status, nivel_acesso):
    db = conectar_bd()
    myc = cursor_on(db)

    #codificando senha
    sen = senha.encode('utf-8')
    salt = bcrypt.gensalt()
    hash_senha = bcrypt.hashpw(sen, salt)

    # Inserindo informações no Banco de dados
    sql = ('INSERT INTO usuario (nome, PASSWORD_HASH, email, telefone, status, nivel_acesso) VALUES (%s, %s, %s, %s, %s, %s)')
    val = (nome, hash_senha, email, telefone, status, nivel_acesso)
    myc.execute(sql, val)
    db.commit()

    turnoff(myc, db)


def login_user(nome, senha):
    db = conectar_bd()
    myc = cursor_on(db)
    sql = 'SELECT * FROM usuario WHERE NOME = %s'
    prc = (nome, )
    sen = senha.encode('utf-8')
    try:
        myc.execute(sql, prc)
        res = myc.fetchone()
    except Exception as erro:
        print(f'Usuário não encontrado! {erro.__class__}')
    else:
        try: 
            if bcrypt.checkpw(sen, res[2].encode('utf-8')):
                turnoff(myc, db)
                return True
            else:
                turnoff(myc, db)
                return False
        except:
            turnoff(myc, db)
            return False
