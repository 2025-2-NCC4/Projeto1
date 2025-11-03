from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import hashlib # Para criptografar senhas
import os

# Inicializa o app Flask
app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_muito_segura'

# --- Configuração do Banco de Dados ---
DATABASE = 'users.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# --- Função para HASH de Senha ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# --- Rota de Cadastro ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        if not nome or not email or not senha:
            flash('Todos os campos são obrigatórios!', 'error')
            return redirect(url_for('login')) # Volta para a home (login/register)

        senha_hash = hash_password(senha)

        try:
            db = get_db()
            db.execute("INSERT INTO users (nome, email, password) VALUES (?, ?, ?)",
                       (nome, email, senha_hash))
            db.commit()
            db.close()
            flash('Conta criada com sucesso! Faça o login.', 'success')
        except sqlite3.IntegrityError:
            flash('Este e-mail já está cadastrado.', 'error')

        return redirect(url_for('login'))

    # Se for GET, apenas redireciona para a home
    return redirect(url_for('login'))

# --- Página de Login ---
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        senha_hash = hash_password(senha)

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        db.close()

        if user and user['password'] == senha_hash:
            session['logged_in'] = True
            session['user_nome'] = user['nome'] # Salva o nome do usuário na sessão
            return redirect(url_for('run_dashboard'))
        else:
            flash('E-mail ou senha inválidos.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

# --- Rota de Logout (Ainda não usamos, mas é bom ter) ---
@app.route('/logout')
def logout():
    session.clear() # Limpa toda a sessão
    flash('Você saiu da sua conta.', 'success')
    return redirect(url_for('login'))

# --- Rota para redirecionar para o Streamlit ---
@app.route('/dashboard')
def run_dashboard():
    if not session.get('logged_in'):
        flash('Você precisa estar logado para ver o dashboard.', 'error')
        return redirect(url_for('login'))

    # Apenas redireciona para o Streamlit (Terminal 2)
    return redirect('http://localhost:8501')

# --- Roda o servidor Flask e Inicializa o DB ---
if __name__ == '__main__':
    # Verifica se o DB já existe, se não, cria
    if not os.path.exists(DATABASE):
        print("Criando o banco de dados...")
        # Precisamos criar o arquivo schema.sql
        # (Vamos fazer isso no próximo passo)
        # Por enquanto, vamos criar a tabela manualmente aqui

        try:
            db = sqlite3.connect(DATABASE)
            cursor = db.cursor()
            cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            );
            """)
            db.commit()
            db.close()
            print("Banco de dados 'users.db' e tabela 'users' criados com sucesso.")
        except Exception as e:
            print(f"Erro ao criar DB: {e}")

    app.run(debug=True, port=5000)