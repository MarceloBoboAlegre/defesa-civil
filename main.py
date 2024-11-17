from flask import Flask, request, render_template, send_file, redirect
from uteis import cadastro, get_markers, gerador_pdf, new_cadastro
from flask_cors import CORS
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os


app = Flask(__name__)
CORS(app)  # Permite CORS para todas as rotas e origens
app.config['SECRET_KEY'] = 'CivDef321'

# Configuração da pasta onde as imagens serão salvas
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Criar a pasta de uploads se não existir
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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
    data = request.form.get('data')
    origem = request.form.get('origem')
    nome = request.form.get('nome')
    documento = request.form.get('documento')
    telefone1 = request.form.get('telefone1')
    telefone2 = request.form.get('telefone2')
    email = request.form.get('email')
    logradouro = request.form.get('logradouro')
    numero = request.form.get('numero')
    bairro = request.form.get('bairro')
    complemento = request.form.get('complemento')
    ponto_referencia = request.form.get('ponto_referencia')
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')
    ocorrencia = request.form.get('ocorrencia')
    prioridade =  request.form.get('prioridade')
    area = request.form.get('area')
    pmrr = request.form.get('pmrr')
    imagens = request.files.getlist('imagens')
    for i in imagens:
        i.save(os.path.join(app.config['UPLOAD_FOLDER'], i.filename))
    try:
        new_cadastro(data, origem, nome, documento, telefone1, telefone2, email, 
              logradouro, numero, bairro, complemento, ponto_referencia, 
              latitude, longitude, ocorrencia, prioridade, area, pmrr, imagens)
        #cadastro(nome, email, latitude, longitude, formato, imagens)
    except:
        print('Erro ao cadastrar')


# Rota para gerar o PDF
@app.route('/gerar_pdf', methods=['GET'])
def gerar_pdf():
    cadastro_nome = request.args.get('nome')
    info = gerador_pdf(cadastro_nome)
    print(info)
    cadastroo = info[0]
    imagens = info[1]
    cadastro_id = cadastroo['id']
    

    # Criando o PDF com reportlab
    c = canvas.Canvas(f'{cadastro_nome}.pdf', pagesize=letter)
    width, height = letter  # width e height são números inteiros agora

    # Título do PDF
    c.drawString(100, height - 50, "Relatório do Cadastro")
    c.drawString(100, height - 70, f"ID: {cadastroo['id']}")
    c.drawString(100, height - 90, f"Nome: {cadastroo['nome']}")
    c.drawString(100, height - 110, f"Email: {cadastroo['email']}")
    c.drawString(100, height - 130, f"Latitude: {cadastroo['latitude']}")
    c.drawString(100, height - 150, f"Longitude: {cadastroo['longitude']}")
    c.drawString(100, height - 170, f"Forma: {cadastroo['formato']}")

    # Adicionando imagens ao PDF
    y_position = height - 210
    for i, img in enumerate(imagens):
        print(img['caminho'])
        c.drawString(100, y_position, f"Imagem {i + 1}")
        try:
            c.drawImage('uploads/'+img['caminho'], 100, y_position - 105, width=100, height=100)
            y_position -= 140  # Espaçamento entre as imagens
        except Exception as e:
            c.drawString(100, y_position - 20, f"Erro ao carregar imagem: {e}")
            y_position -= 40  # Ajuste se ocorrer erro

    # Salvando o PDF
    c.save()
    return send_file(f'{cadastro_nome}.pdf', as_attachment=True, download_name=f"Cadastro_{cadastroo['nome']}.pdf", mimetype="application/pdf")

# Iniciar o servidor Flask
if __name__ == '__main__':
    app.run(debug=True)
