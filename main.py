from flask import Flask, request, render_template, send_file
import mysql.connector
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io


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

    sql = "SELECT nome, email, latitude, longitude FROM cadastros"
    myc.execute(sql)
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
    quant = len(marca)
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


@app.route('/gerar_pdf', methods=['GET'])
def gerar_pdf():
    db = conectar_bd('localhost', 'root', '', 'defesa')
    myc = db.cursor(dictionary=True)

    # Consulta os dados cadastrados no banco de dados
    query = "SELECT nome, email, latitude, longitude FROM cadastros"
    myc.execute(query)
    cadastros = myc.fetchall()

    # Fechando a conexão com o banco de dados
    turnoff(myc, db)

    # Criando o PDF em memória
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setTitle("Relatório de Cadastros")

    # Título
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(100, 800, "Relatório de Cadastros")

    # Cabeçalho das colunas
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, 750, "Nome")
    pdf.drawString(200, 750, "Email")
    pdf.drawString(350, 750, "Latitude")
    pdf.drawString(450, 750, "Longitude")

    # Conteúdo das colunas
    pdf.setFont("Helvetica", 10)
    y = 730  # Coordenada vertical inicial
    for cad in cadastros:
        pdf.drawString(50, y, cad['nome'])
        pdf.drawString(200, y, cad['email'])
        pdf.drawString(350, y, str(cad['latitude']))
        pdf.drawString(450, y, str(cad['longitude']))
        y -= 20  # Movendo para a próxima linha

    pdf.save()

    # Movendo o ponteiro para o início do buffer
    buffer.seek(0)

    # Retornando o PDF como resposta
    return send_file(buffer, as_attachment=True, download_name="relatorio_cadastros.pdf", mimetype='application/pdf')


# Iniciar o servidor Flask
if __name__ == '__main__':
    app.run(debug=True)
