from core.imports import *
from core.userAuth import *
from core.decorators import *

admin_bp = Blueprint('admin', __name__, template_folder='templates', static_folder='static')

@admin_bp.route('/homeAdmin')
@login_required
@admin_required
def homeAdmin():
    return render_template('homeAdmin.html', current_user=current_user.nome)

@admin_bp.route('/cadastrar')
def cadastrar():
    return render_template('cadastrar_func.html')  

@admin_bp.route('/cadastrar_funcionario', methods=['POST'])
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
            return redirect(url_for('admin.homeAdmin'))
        except Exception as e:
            erro = f"Erro ao cadastrar funcionário: {e}"
            return render_template('cadastrar_func.html', erro=erro)

@admin_bp.route('/excluir')
def excluir():
    return render_template('excluir_func.html')

@admin_bp.route('/excluir_funcionario', methods=['POST'])
def excluir_funcionario():
    id = request.form['id']
    
    conn = get_some_connection('funcionario')
    cursor = conn.cursor()
    cursor.execute('UPDATE funcionario SET ativo = 0 WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin.homeAdmin'))

@admin_bp.route('/listar')
def listar():
    conn = get_some_connection('funcionario')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM funcionario WHERE ativo = 1')
    funcionarios = cursor.fetchall()
    conn.close()

    return render_template('listar_funcionario.html', funcionarios=funcionarios)