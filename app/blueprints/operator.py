from core.imports import *
from core.userAuth import Funcionario
from core.decorators import operador_required
from database.db import *
from datetime import datetime


operator_bp = Blueprint('operator', __name__, template_folder='templates', static_folder='static')

@operator_bp.route('/homeOperator', methods=['GET'])
@login_required
@operador_required
def homeOperator():
    pedidos = executar_sql('''
        SELECT id,
               nome,
               preco,
               nota,
               status,
               formaDePagamento,
               dataCriacao
        FROM vendas
        WHERE status = "aberto"
        ORDER BY id DESC
    ''')
    
    notas = executar_sql('''
        SELECT id, conteudo, data_mod 
        FROM notes 
        WHERE ativo = 1 
        ORDER BY data_mod DESC
    ''')

    if isinstance(notas, dict) and 'erro' in notas:
        print("Erro ao buscar notas:", notas['erro'])
        notas = []

    return render_template(
        'homeOperator.html', 
        notas=notas, 
        pedidos=pedidos, 
        user=current_user
    )



@operator_bp.route('/salvarNota', methods=['POST'])
@login_required
def mandarNota():
    tempNote = (request.form.get('conteudo') or '').strip()
    if not tempNote:
        return redirect(url_for('operator.homeOperator'))
    add_res = addNote(tempNote)
    if isinstance(add_res, dict) and 'erro' in add_res:
        print("Erro ao inserir nota:", add_res['erro'])

    return redirect(url_for('operator.homeOperator'))

@operator_bp.route('/removerNota', methods=['POST'])
@login_required
def rmNote():
    executar_sql("DELETE FROM notes WHERE id = ?", (request.form['id'],))
    return redirect(url_for('operator.homeOperator'))

@operator_bp.route('/cadastrarPedido', methods=['GET', 'POST'])
@login_required
def cadastroPedido():
    if request.method == 'POST':
        nomeItem = request.form.get('nome')
        precoItem = request.form.get('preco')
        notaItem = request.form.get('nota') or None
        formaDePagamento = request.form.get('formaDePagamento')

        # 👉 gera data/hora em horário local (string)
        data_criacao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        executar_sql('''
            INSERT INTO vendas (nome, preco, nota, status, formaDePagamento, dataCriacao)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (nomeItem, precoItem, notaItem, "aberto", formaDePagamento, data_criacao))
        
        return redirect(url_for('operator.homeOperator'))
    return redirect(url_for('operator.homeOperator'))

@operator_bp.route('/fecharPedido', methods=['GET', 'POST'])
@login_required
def fecharPedido():
    pedido_id = request.form.get('id')
    executar_sql('UPDATE vendas SET status = ? WHERE id = ?', ("fechado", pedido_id))
    return redirect(url_for('operator.homeOperator'))

@operator_bp.route('/registrarSangria', methods=['GET', 'POST'])
@login_required
def registrarSangria():
    if request.method == 'POST':
        valorSangria = request.form.get('valor')
        motivo       = request.form.get('motivo')
        usuario      = current_user.nome
        data         = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        executar_sql('INSERT INTO sangrias (valor, motivo, usuario, data) VALUES (?, ?, ?, ?)',
                    (valorSangria, motivo, usuario, data))
        
        return redirect(url_for('operator.homeOperator'))
    return redirect(url_for("operator.homeOperator"))