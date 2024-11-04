from flask import Flask, request, render_template, send_file, redirect
from uteis import cadastro, get_markers, gerador_pdf
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


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
    formato =  request.form.get('formato')
    imagens = request.files.getlist('imagens')
    cadastro(nome, email, latitude, longitude, formato, imagens)


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
    """
    y_position = height - 210
    for i, img in enumerate(imagens):
        c.drawString(100, y_position, f"Imagem {i + 1}")
        try:
            c.drawImage(img['caminho'], 100, y_position - 100, width=100, height=100)
            y_position -= 140  # Espaçamento entre as imagens
        except Exception as e:
            c.drawString(100, y_position - 20, f"Erro ao carregar imagem: {e}")
            y_position -= 40  # Ajuste se ocorrer erro
    """

    # Finalizando o PDF
    c.save()

    #return send_file(f'{cadastro_nome}.pdf', as_attachment=True, download_name=f"Cadastro_{cadastroo['nome']}.pdf", mimetype="application/pdf")
    return redirect('/')

# Iniciar o servidor Flask
if __name__ == '__main__':
    app.run(debug=True)
