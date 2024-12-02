from flask import Flask, request, render_template, send_file, redirect
from uteis import cadastro, get_markers, gerador_pdf
from flask_cors import CORS
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
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
    temp = get_markers()

    # Transformando as tuplas em listas para poder transformar a data em string
    marca = []
    temp2 = []
    for t in temp:
        for i in t:
            temp2.append(i)
        temp2[1] = temp2[1].strftime('%d/%m/%Y')
        marca.append(temp2[:])
        temp2.clear()
    tecnico = ['Avaliação de risco estrutural', 'Avaliação de risco geológico', 'Avaliação de risco hidrológico',
               'Vistoria em equipamento público', 'Vistoria em leito de rio']
    tecnico_operacional = ['Monitoramento', 'Risco de Queda de árvore']
    operacional = ['Manejo de animal silvestre', 'Alagamento/Inundação/Enchente', 'Deslizamento', 'Destelhamento',
                   'Incêndio em vegetação', 'Incêndio em edificação', 'Apoio Marítmo', 'Outros']
    # Passando o tipo de marcador a ser usado com base na situacao e tipo_ocorrencia do banco de dados
    for m in marca:
        if m[5] in tecnico:
            if m[4] == 'Concluído':
                m[4] = 'greenSquare'
            elif m[4] == 'Visitado':
                m[4] = 'yellowSquare'
            else:
                m[4] = 'redSquare'
        elif m[5] in tecnico_operacional:
            if m[4] == 'Concluído':
                m[4] = 'greenTriangle'
            elif m[4] == 'Visitado':
                m[4] = 'yellowTriangle'
            else:
                m[4] = 'redTriangle'
        else:
            if m[4] == 'Concluído':
                m[4] = 'greenCircle'
            elif m[4] == 'Visitado':
                m[4] = 'yellowCircle'
            else:
                m[4] = 'redCircle'
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
    tipo_ocorrencia = request.form.get('tipo_ocorrencia')
    situacao = request.form.get('situacao')
    area = request.form.get('area')
    pmrr = request.form.get('pmrr')
    imagens = request.files.getlist('imagens')
    for i in imagens:
        i.save(os.path.join(app.config['UPLOAD_FOLDER'], i.filename))
    try:
        cadastro(data, origem, nome, documento, telefone1, telefone2, email, 
            logradouro, numero, bairro, complemento, ponto_referencia, 
            latitude, longitude, ocorrencia, tipo_ocorrencia, situacao, area, pmrr, imagens)
    except:
        print('Erro ao cadastrar')


# Rota para gerar o PDF
@app.route('/gerar_pdf', methods=['GET'])
def gerar_pdf():
    cadastro_id = request.args.get('id')
    info = gerador_pdf(cadastro_id)

    cadastroo = info[0]
    imagens = info[1]
    cadastro_nome = cadastroo['nome']
    

    # Criando o PDF com reportlab
    c = canvas.Canvas(f'{cadastro_nome}.pdf', pagesize=letter)
    width, height = letter  # width e height são números inteiros agora

    # Título do PDF
    c.drawString(100, height - 50, "Relatório do Cadastro")
    altura = 50
    for k, v in cadastroo.items():
        if k == 'ocorrencia':
            altura += 20
            lines = simpleSplit(v, 'Helvetica', 12, width - 120)
            c.drawString(100, height - altura, f"{k}:")
            for line in lines:
                altura += 20
                c.drawString(100, height - altura, f"{line}")
        else:
            altura += 20
            c.drawString(100, height - altura, f"{k}: {v}")
    

    # Adicionando imagens ao PDF
    y_position = height - (altura + 20)
    for i, img in enumerate(imagens):
        c.drawString(100, y_position, f"Imagem {i + 1}")
        try:
            c.drawImage('uploads/'+img['caminho'], 100, y_position - 105, width=100, height=100)
            y_position -= 120  # Espaçamento entre as imagens
        except Exception as e:
            c.drawString(100, y_position - 20, f"Erro ao carregar imagem: {e}")
            y_position -= 40  # Ajuste se ocorrer erro

    # Salvando o PDF
    c.save()
    return send_file(f'{cadastro_nome}.pdf', as_attachment=True, download_name=f"Cadastro_{cadastroo['nome']}.pdf", mimetype="application/pdf")


# Iniciar o servidor Flask
if __name__ == '__main__':
    app.run(debug=True)
