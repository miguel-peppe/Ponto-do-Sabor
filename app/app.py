from core.imports import *
from core.userAuth import Funcionario
from core.decorators import admin_required, operador_required
from database.db import *
from flask_login import LoginManager
from blueprints.admin import admin_bp
from blueprints.operator import operator_bp
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = 'chave-secreta'  
app.register_blueprint(admin_bp)
app.register_blueprint(operator_bp)
login_manager = LoginManager()
login_manager.login_view = 'login'  # redireciona para /login se não logado
login_manager.init_app(app)

@app.route('/')
def home1():
    # return render_template('home.html')
    return redirect(url_for('login'))

""" ======================== Login ======================== """
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        cpf = request.form['cpf']
        senha = request.form['senha']
        
        conn = get_some_connection('funcionario')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM funcionario WHERE cpf = ? AND ativo = 1", (cpf,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['senha_hash'], senha):
            login_user(Funcionario(user['id'], user['nome'], user['cpf'], user['cargo']))
            if user['cargo'] == 'admin':
                return redirect(url_for('admin.homeAdmin'))
            elif user['cargo'] == 'operador':
                return redirect(url_for('operator.homeOperator'))

        return render_template('login.html', erro="CPF ou senha inválidos.")

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
    

@login_manager.user_loader
def load_user(user_id):
    conn = get_some_connection('funcionario')
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, cpf, cargo FROM funcionario WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    if user:
        return Funcionario(user['id'], user['nome'], user['cpf'], user['cargo'])
    return None

"""======================== runner' ========================"""
if __name__ == "__main__":
    db_init_all()  # Cria tabela se não existir
    app.run(debug=True, port=8080)