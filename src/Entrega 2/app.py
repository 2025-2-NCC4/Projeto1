from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import hashlib
import os

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_muito_segura'
DATABASE = 'users.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        perfil = request.form['perfil']

        senha_hash = hash_password(senha)
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ? AND perfil = ?", (email, perfil)).fetchone()
        db.close()

        if user and user['password'] == senha_hash:
            session['logged_in'] = True
            session['user_nome'] = user['nome']
            session['user_perfil'] = user['perfil']
            return redirect(url_for('run_dashboard'))
        else:
            flash('E-mail, senha ou perfil inválidos.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- Rota de Redirecionamento (MODIFICADA) ---
@app.route('/dashboard')
def run_dashboard():
    if not session.get('logged_in'):
        flash('Você precisa estar logado para ver o dashboard.', 'error')
        return redirect(url_for('login'))

    # Pega o perfil salvo na sessão
    perfil = session.get('user_perfil', 'CEO') # Padrão 'CEO' se algo der errado

    # Redireciona para o Streamlit E PASSA O PERFIL NA URL
    return redirect(f'http://localhost:8501/?profile={perfil}')

# --- Roda o servidor Flask e Inicializa o DB ---
def init_db_com_usuarios():
    print("Criando o banco de dados 'users.db'...")
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT NOT NULL,
        password TEXT NOT NULL,
        perfil TEXT NOT NULL,
        UNIQUE(email, perfil)
    );
    """)

    senha_hash_padrao = hash_password('123')
    try:
        cursor.execute("INSERT INTO users (nome, email, password, perfil) VALUES (?, ?, ?, ?)", 
                       ('Admin CEO', 'ceo@picmoney.com', senha_hash_padrao, 'CEO'))
        cursor.execute("INSERT INTO users (nome, email, password, perfil) VALUES (?, ?, ?, ?)", 
                       ('Admin CFO', 'cfo@picmoney.com', senha_hash_padrao, 'CFO'))
    except sqlite3.IntegrityError:
        print("Usuários padrão já existem.")

    db.commit()
    db.close()
    print("Banco de dados e usuários padrão criados com sucesso.")
    print("---")
    print("Logins de Teste (senha: 123):")
    print("CEO: ceo@picmoney.com")
    print("CFO: cfo@picmoney.com")
    print("---")


if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db_com_usuarios()
    app.run(debug=True, port=5000)