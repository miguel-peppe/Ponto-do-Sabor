from core.imports import *
from core.userAuth import Funcionario
from core.decorators import operador_required
from database.db import *

operator_bp = Blueprint('operator', __name__, template_folder='templates', static_folder='static')

@login_required
@operator_bp.route('/homeOperator', methods=['GET'])
@operator_bp.route('/homeOperator', methods=['GET'])
@login_required
def homeOperator():
    notas = executar_sql('SELECT id, conteudo, data_mod FROM notes WHERE ativo = 1 ORDER BY data_mod DESC')
    if isinstance(notas, dict) and 'erro' in notas:
        print("Erro ao buscar notas:", notas['erro'])
        notas = []
    return render_template('homeOperator.html', notas=notas)

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
def rmNote():
    executar_sql("DELETE FROM notes WHERE id = ?", (request.form['id'],))
    return redirect(url_for('operator.homeOperator'))