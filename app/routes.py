from app import app
from flask import render_template, request
from app.database.alerta import *
from app.database.arquivo import *
from app.database.historico import *

@app.route('/')
def index():
    return render_template('login.html')

## notificacoes, historicos e avaliacoes
## Routes modificados para receber dados
@app.route('/historico_geral')
def historico_geral():

    periodo = request.args.get('periodo', 'mes')
    tipo = request.args.get('tipo', 'todos')
    pagamento = request.args.get('pagamento', 'todos')

    historico = listar_historico(
        periodo=periodo,
        tipo=tipo,
        pagamento=pagamento
    )

    return render_template(
        'historico_geral.html',
        historico=historico,
        periodo=periodo,
        tipo=tipo,
        pagamento=pagamento
    )

@app.route('/historico_aluno/<int:id_aluno>')
def historico_aluno(id_aluno):
    data_aluno = listar_historico_aluno(id_aluno) 
    return render_template( 'historico_aluno.html', data_aluno=data_aluno )

@app.route('/notificacoes')
def notificacoes():

    alertas = listar_alertas()
    nao_lidas = contar_nao_lidas()

    return render_template(
        'notificacoes.html',
        alertas=alertas,
        nao_lidas=nao_lidas
    )

@app.route('/notificacoes/<int:id_alerta>/visualizar', methods=['PATCH'])
def visualizar_notificacao(id_alerta):
    visualizar_alerta(id_alerta)
    return '', 204

@app.route('/avaliacoes_usuario')
def avaliacoes_usuario():
    avaliacoes = listar_avaliacoes()
    return render_template('avaliacoes_usuario.html',avaliacoes=avaliacoes)

@app.route('/avaliacoes/excluir/<int:id_avaliacao>', methods=['POST'])
def excluir_avaliacao_rota(id_avaliacao):

    excluir_avaliacao(id_avaliacao)

    return redirect(url_for('avaliacoes'))
## fim notif, avaliacao e historicos

@app.route('/presenca')
def presenca():
    return render_template('presenca.html')


@app.route('/usuarios')
def usuarios():
    return render_template('usuarios.html')

@app.route('/informacoes_usuario')
def informacoes_usuario():
    return render_template('informacoes_usuario.html')


@app.route('/editar_usuario')
def editar_usuario():
    return render_template('editar_usuario.html')

@app.route('/cadastrar_usuario')
def cadastrar_usuario():
    return render_template('cadastrar_usuario.html')