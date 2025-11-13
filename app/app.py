from core.imports import *
from core.userAuth import Funcionario
from core.decorators import admin_required, operador_required
from database.db import *
from flask_login import LoginManager

#senha_hash

app = Flask(__name__)
app.secret_key = 'chave-secreta'  

login_manager = LoginManager()
login_manager.login_view = 'login'  # redireciona para /login se não logado
login_manager.init_app(app)

@app.route('/')
def home1():
    # return render_template('home.html')
    return redirect(url_for('login'))

@login_required
@admin_required
@app.route('/homeAdmin')
def homeAdmin():
    return render_template('homeAdmin.html', current_user=current_user.nome)

@app.route('/homeOperator', methods=['GET'])
@login_required
def homeOperator():
    notas = executar_sql('SELECT id, conteudo, data_mod FROM notes WHERE ativo = 1 ORDER BY data_mod DESC')
    if isinstance(notas, dict) and 'erro' in notas:
        print("Erro ao buscar notas:", notas['erro'])
        notas = []
    return render_template('homeOperator.html', notas=notas)

@app.route('/salvarNota', methods=['POST'])
@login_required
def mandarNota():
    tempNote = (request.form.get('conteudo') or '').strip()
    if not tempNote:
        return redirect(url_for('homeOperator'))

    add_res = addNote(tempNote)
    if isinstance(add_res, dict) and 'erro' in add_res:
        print("Erro ao inserir nota:", add_res['erro'])

    return redirect(url_for('homeOperator'))

@app.route('/removerNota', methods=['POST'])
def rmNote():
    executar_sql("UPDATE notes SET ativo = 0 WHERE id = ?", (request.form['id'],))
    return redirect(url_for('homeOperator'))
""" ======================== Funcionarios ======================== """
@app.route('/cadastrar')
def cadastrar():
    return render_template('cadastrar_func.html')  

@app.route('/cadastrar_funcionario', methods=['POST'])
def cadastrar_funcionario():
    if request.method == 'POST':
        nome = request.form['nome']
        cpf = request.form['cpf']
        cargo = request.form['cargo']
        senha = request.form['senha']
        data = request.form.get('data_contratacao')
        senha_hash = generate_password_hash(senha)

        if not validar_cpf(cpf):
            erro = "CPF inválido. Verifique e tente novamente."
            return render_template('cadastrar_func.html', erro=erro, nome=nome, cpf=cpf, cargo=cargo)

        try:
            add_funcionario(nome, cpf, cargo, senha_hash, data)
            return redirect(url_for('homeAdmin'))
        except Exception as e:
            erro = f"Erro ao cadastrar funcionário: {e}"
            return render_template('cadastrar_func.html', erro=erro)

@app.route('/excluir')
def excluir():
    return render_template('excluir_func.html')

@app.route('/excluir_funcionario', methods=['POST'])
def excluir_funcionario():
    id = request.form['id']
    
    conn = get_connect()
    cursor = conn.cursor()
    cursor.execute('UPDATE funcionario SET ativo = 0 WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('homeAdmin'))

@app.route('/listar')
def listar():
    conn = get_connect()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM funcionario WHERE ativo = 1')
    funcionarios = cursor.fetchall()
    conn.close()

    return render_template('listar_funcionario.html', funcionarios=funcionarios)


""" ======================== Login ======================== """
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        cpf = request.form['cpf']
        senha = request.form['senha']
        
        conn = get_connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM funcionario WHERE cpf = ? AND ativo = 1", (cpf,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['senha_hash'], senha):
            login_user(Funcionario(user['id'], user['nome'], user['cpf'], user['cargo']))
            if user['cargo'] == 'admin':
                return redirect(url_for('homeAdmin'))
            elif user['cargo'] == 'operador':
                return redirect(url_for('homeOperator'))

        return render_template('login.html', erro="CPF ou senha inválidos.")

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
    

@login_manager.user_loader
def load_user(user_id):
    conn = get_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, cpf, cargo FROM funcionario WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    if user:
        return Funcionario(user['id'], user['nome'], user['cpf'], user['cargo'])
    return None


"""======================== runner' ========================"""
if __name__ == "__main__":
    db_init()  # Cria tabela se não existir
    db_init_note()
    initPedido()
    app.run(debug=True, port=8080)
