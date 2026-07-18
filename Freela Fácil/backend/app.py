from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

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

class Vagas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contratante_id = db.Column(db.Integer, db.ForeignKey('contratante.id'), nullable=False)
    criador = db.relationship('Contratante', backref='vagas_criadas')
    titulo = db.Column(db.String(100), nullable=False)
    remuneracao = db.Column(db.String(50), nullable=False)
    descricao = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(20), default='Aberta')
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

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
        tipo_usuario = 'freelancer'
        if not usuario:
            usuario = Contratante.query.filter_by(email=email_digitado).first()
            tipo_usuario = 'contratante'
        
        if usuario and check_password_hash(usuario.senha, senha_digitada):
            session['usuario_id'] = usuario.id
            session['tipo'] = tipo_usuario
            return redirect(url_for('mostrar_vaga_tela'))
        
        else:
            return "E-mail ou senha incorretos. Tente novamente."
            

@app.route('/botao_resetsenha')
def botao_resetsenha():
    return render_template('reset-senha.html')

@app.route('/criar_vaga', methods=['GET', 'POST'])
def criar_vaga():
    if request.method == 'GET':
        return render_template('contratante/criar-vaga.html')
    elif request.method == 'POST':
        if 'usuario_id' not in session or session['tipo'] != 'contratante':
            flash("Você precisa ser um contratante para publicar uma vaga!")
            return redirect(url_for('login'))
        
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        remuneracao = request.form['valor']
        status = request.form['status']
        
        id_contratante = session['usuario_id']
        
        nova_vaga = Vagas(
            contratante_id = id_contratante,
            titulo = titulo,
            descricao = descricao,
            remuneracao = remuneracao,
            status = status
        )
        
        db.session.add(nova_vaga)
        db.session.commit()
        
        flash("Vaga publicada!")
        return redirect(url_for('minhas_vagas'))
    
@app.route('/botao_perfil')
def botao_perfil():
    if 'usuario_id' not in session:
        flash("Você precisa estar logado para ver o seu perfil.")
        return redirect(url_for('login'))
    
    tipo_usuario = session.get('tipo')
    
    if tipo_usuario == 'freelancer':
        return render_template('freelancer/perfilfree.html')
    elif tipo_usuario == 'contratante':
        return render_template('contratante/perfilcont.html')

    
@app.route('/mostrar_vagas_tela')
def mostrar_vaga_tela():
    if 'usuario_id' not in session:
        flash("Você precisa estar logado para acessar as vagas.")
        return redirect(url_for('login'))
        
    todas_vagas = Vagas.query.filter_by(status='aberta').all()
    
    return render_template('vagas/tela-inicial.html', vagas_na_tela=todas_vagas)

@app.route('/minhas_vagas')
def minhas_vagas():
    if 'usuario_id' not in session or session.get('tipo') != 'contratante':
        flash("Você precisa estar logado como contratante para acessar as vagas.")
        return redirect(url_for('login'))
    
    id_contratante = session['usuario_id']
    minhas_vagas_banco = Vagas.query.filter_by(contratante_id=id_contratante).all()
    
    return render_template('contratante/vagaspubli.html', vagas_na_tela=minhas_vagas_banco)

@app.route('/detalhes-vaga/<int:id>')
def detalhes_vaga(id):  
    vaga_clicada = Vagas.query.get(id)

    if not vaga_clicada:
        return "Vaga não encontrada!", 404
    
    return render_template('vagas/detalhes-vaga.html', vaga=vaga_clicada)

@app.route('/edit_vaga/<int:id>', methods=['GET', 'POST'])
def edit_vaga(id):
    vaga_selecionada = Vagas.query.get(id)
    if not vaga_selecionada:
        return "Vaga não encontrada!", 404
    
    if vaga_selecionada.contratante_id != session ['usuario_id']:
        flash("Você não tem permissão para editar esta vaga!")
        return redirect(url_for('minhas_vagas'))
    
    if request.method == 'GET':
        return render_template('contratante/edit-vaga.html',
        vaga=vaga_selecionada)
        
    if request.method == 'POST':
        if 'usuario_id' not in session or session.get('tipo') != 'contratante':
            flash("Você precisa ser um contratante para editar uma vaga!")
            return redirect(url_for('login'))
        
        vaga_selecionada.titulo = request.form['titulo']
        vaga_selecionada.descricao = request.form['descricao']
        vaga_selecionada.remuneracao = request.form['remuneracao']
        vaga_selecionada.status = request.form['status']
    
        db.session.commit()
        
        flash("Vaga editada com sucesso!")
        return redirect(url_for('minhas_vagas'))
    
    return render_template('contratante/edit-vaga.html', vaga=vaga_selecionada)

@app.route('/excluir_vaga/<int:id>')
def excluir_vaga(id):
    vaga = Vagas.query.get(id)
    
    if not vaga:
        return "Vaga não encontrada!", 404
    
    if vaga.contratante_id != session ['usuario_id']:
        flash("Você não tem permissão para editar esta vaga!")        
        return redirect(url_for('minhas_vagas'))
    
    if 'usuario_id' not in session or session.get('tipo') != 'contratante':
        flash("Você precisa ser um contratante para editar uma vaga!")
        return redirect(url_for('login'))
    
    db.session.delete(vaga)
    db.session.commit()
    
    flash("Vaga excluída com sucesso!")
    return redirect(url_for('minhas_vagas'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    
    