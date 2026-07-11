from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = '80291f20b2d0181711a34781a99dd5ebe5ee07c7296c1948'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///freela.db'

db = SQLAlchemy(app)

class Freelancer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    
class Contratante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cnpj = db.Column(db.String(18), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)

# --- ROTAS DO PROJETO ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastro_tipo')
def cadastro_tipo(): # É ESTE NOME QUE O URL_FOR USA
    return render_template('cadastro-tipo.html')

@app.route('/botao_freelancer')
def botao_freelancer():
    return render_template('freelancer/cadastro-freelancer.html')

@app.route('/botao_contratante')
def botao_contratante():
    return render_template('contratante/cadastro-contratante.html')

@app.route('/registrar_freelancer',  methods=['GET', 'POST'])
def registrar_freela():
    if request.method == 'GET':
        return render_template('freelancer/cadastro-freelancer.html')
    elif request.method == 'POST':
        nome = request.form['nome']
        cpf = request.form['cpf']
        email = request.form['email']
        senha = request.form['senha']
        repeatsenha = request.form['repita_senha']
        
        if len(nome.strip().split()) < 2:
            flash ("Por favor, digite seu nome e sobrenome.")
            return render_template('freelancer/cadastro-freelancer.html')
        
        cpf_limpo = ''.join(filter(str.isdigit, cpf))
        if len(cpf_limpo) != 11 or not cpf.isdigit():
            flash("Cpf inválido! Deve conter exatamente 11 dígitos!")
            return render_template('freelancer/cadastro-freelancer.html')
        
        if len(senha) < 8 or not any(c.isupper() for c in senha) or not any(c.islower() for c in senha):
            flash("A senha deve ter pelo menos 8 caracteres, contendo letras maiúsculas e minúsculas.")
            return render_template('freelancer/cadastro-freelancer.html')
        
        if senha != repeatsenha:
            flash ("As senhas não coincidem!")
            return render_template('freelancer/cadastro-freelancer.html')
        
        senha_criptografada = generate_password_hash(senha) # Transforma a senha em um "hash" (texto embaralhado impossível de reverter)
        
        try:
            freelancer = Freelancer(nome=nome, cpf=cpf, email=email, senha=senha_criptografada)
            db.session.add(freelancer)
            db.session.commit()
            flash("Cadastro realizado com sucesso!", "success")
            return redirect(url_for('index'))
        
        except Exception as err:
            db.session.rollback() # Desfaz a tentativa para não deixar o banco de dados travado
            flash("Ocorreu um erro no servidor. Tente novamente mais tarde.")
            print(f"Erro no banco de dados: {err}") # Para o seu log de debug
            return render_template('freelancer/cadastro-freelancer.html')
        
@app.route('/registrar_contratante', methods=['GET', 'POST'])
def registrar_contratante():
    if request.method == 'GET':
        return render_template('contratante/cadastro-contratante.html')
    elif request.method == 'POST':
        nome = request.form['nome']
        cnpj = request.form['cnpj']
        email = request.form['email']
        senha = request.form['senha']
        repeatsenha = request.form['repita-senha']
        
        if senha != repeatsenha:
            return "As senhas não coincidem!"

        senha_criptografada = generate_password_hash(senha)
        
        contratante = Contratante(nome=nome, cnpj=cnpj, email=email, senha=senha_criptografada)
        db.session.add(contratante)
        db.session.commit()
        
        return redirect(url_for('index'))
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        email_digitado = request.form['email']
        senha_digitada = request.form['senha']
        
        usuario = Freelancer.query.filter_by(email=email_digitado).first()
        if not usuario:
            usuario = Contratante.query.filter_by(email=email_digitado).first()
        
        if usuario and check_password_hash(usuario.senha, senha_digitada):
            return render_template('vagas/tela-inicial.html')
        
        else:
            return "E-mail ou senha incorretos. Tente novamente."
            

@app.route('/botao_resetsenha')
def botao_resetsenha():
    return render_template('reset-senha.html')



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)