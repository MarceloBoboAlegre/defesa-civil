from flask import Flask, request, render_template
import mysql.connector
from flask_cors import CORS


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


def get_markers():
    db = conectar_bd('localhost', 'root', '', 'defesa')
    myc = cursor_on(db)

    query = "SELECT nome, email, latitude, longitude FROM cadastros"
    myc.execute(query)
    markers = myc.fetchall()

    turnoff(myc, db)

    lista = list(markers)
    return lista


app = Flask(__name__)
app.config['SECRET_KEY'] = 'CivDef321'

# Rota padrão
@app.route('/')
def home():
    marca = get_markers()
    print(marca)
    quant = len(marca)
    print(quant)
    final = [quant, marca]
    return render_template('index.html', marcador=final)

# Rota para receber os dados do formulário e cadastrar no banco de dados
@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    # Pegar os dados enviados pelo formulário
    nome = request.form.get('nome')
    email = request.form.get('email')
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')
    cadastro(nome, email, latitude, longitude)


# Iniciar o servidor Flask
if __name__ == '__main__':
    app.run(debug=True)
