from flask import Flask, request, render_template
from uteis import cadastro, get_markers


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
    cadastro(nome, email, latitude, longitude, formato)


# Iniciar o servidor Flask
if __name__ == '__main__':
    app.run(debug=True)
