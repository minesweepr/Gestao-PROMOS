from datetime import date
from flask import render_template, request, jsonify, session, redirect, url_for
from app import app
from app.auth import login_required
from app.database.supabase import supabase, supabase_admin
from app.utils.formatadores import formatar_label, montar_registro

from app.model.aluno import aluno_listar_todos, aluno_listar_por_id
from app.model.usuario import usuario_listar_todos, usuario_listar_por_id
from app.model.historico import listar_historico, listar_historico_aluno
from app.model.alerta import contar_nao_lidas, listar_alertas, visualizar_alerta
from app.model.arquivo import excluir_avaliacao, listar_avaliacoes
from app.model.presenca import listar_presencas_hoje, presenca_aluno_marcar, presenca_aluno_desmarcar

@app.route('/cadastrar_usuario', methods=['GET', 'POST'])
@login_required
def cadastrar_usuario():
    # Trava Backend: Apenas Administradores podem acessar esta rota
    if session.get("usuario_cargo") != "ADMINISTRADOR":
        if request.method == 'POST':
            return jsonify({"sucesso": False, "mensagem": "Acesso negado: Apenas administradores podem cadastrar usuários."}), 403
        return redirect(url_for('presenca'))

    if request.method == 'POST':
        perfil = request.form.get('perfil')
        nome = request.form.get('nome')
        cpf = request.form.get('cpf')

        if not cpf or len(cpf) != 11 or not cpf.isdigit():
            return jsonify({"sucesso": False, "mensagem": "O CPF deve conter exatamente 11 números."}), 400

        try:
            # 1. CADASTRO DE USUÁRIO DO SISTEMA (ADMINISTRADOR / ESTAGIARIO)
            if perfil in ['ADMINISTRADOR', 'ESTAGIARIO']:
                email = request.form.get('email')
                senha = request.form.get('senha')

                if not senha or len(senha) < 6:
                    return jsonify({"sucesso": False, "mensagem": "A senha deve ter no mínimo 6 caracteres."}), 400

                res_auth = supabase_admin.auth.admin.create_user({
                    "email": email,
                    "password": senha,
                    "email_confirm": True,
                    "user_metadata": {"nome": nome, "cargo": perfil, "cpf": cpf}
                })

                auth_user_id = res_auth.user.id if res_auth and res_auth.user else None

                dados_usuario = {
                    "nome": nome,
                    "cpf": cpf,
                    "email": email,
                    "senha_hash": "AUTH_SUPABASE",
                    "cargo": perfil,
                    "status": "ATIVO",
                    "auth_user_id": auth_user_id
                }

                supabase_admin.table('usuario').insert(dados_usuario).execute()
                return jsonify({"sucesso": True, "mensagem": f"Usuário ({perfil.title()}) cadastrado com sucesso!"})

            # 2. CADASTRO DE ALUNO
            elif perfil == 'ALUNO':
                telefone = request.form.get('telefone')
                email_aluno = request.form.get('email_aluno')
                dnasc = request.form.get('dnasc')
                tipo_aluno = request.form.get('tipo_aluno')

                dados_aluno = {
                    "nome": nome,
                    "cpf": cpf,
                    "telefone": telefone if telefone else None,
                    "email": email_aluno if email_aluno else None,
                    "data_nascimento": dnasc if dnasc else None,
                    "data_entrada": str(date.today()),
                    "tipo_aluno": tipo_aluno,
                    "situacao": "ATIVO"
                }

                supabase_admin.table('aluno').insert(dados_aluno).execute()
                return jsonify({"sucesso": True, "mensagem": "Aluno cadastrado com sucesso!"})

            else:
                return jsonify({"sucesso": False, "mensagem": "Selecione um perfil válido."}), 400

        except Exception as erro:
            print("Erro no cadastro:", erro)
            msg_erro = str(erro)
            if "Password should be at least 6 characters" in msg_erro:
                msg_erro = "A senha deve conter no mínimo 6 caracteres."
            elif "duplicate key value" in msg_erro or "23505" in msg_erro:
                msg_erro = "Já existe um registro cadastrado com este CPF ou E-mail."
               
            return jsonify({"sucesso": False, "mensagem": f"Erro no servidor: {msg_erro}"}), 500

    return render_template('cadastrar_usuario.html')

@app.route('/presenca')
@login_required
def presenca():
    alunos=[{'id_aluno': a['id_aluno'], 'nome': a['nome']} for a in aluno_listar_todos('ATIVO')]
    ids_presenca={p['id_aluno'] for p in listar_presencas_hoje()}

    for aluno in alunos:
        aluno['presente']=aluno['id_aluno'] in ids_presenca

    return render_template('presenca.html', alunos=alunos)

@app.route('/presenca/marcar/<int:id_aluno>', methods=['POST'])
@login_required
def presenca_marcar(id_aluno):
    presenca_aluno_marcar(id_aluno=id_aluno, id_usuario=session.get("id_usuario"))
    return redirect(url_for('presenca'))

@app.route('/presenca/desmarcar/<int:id_aluno>', methods=['POST'])
@login_required
def presenca_desmarcar(id_aluno):
    presenca_aluno_desmarcar(id_aluno)
    return redirect(url_for('presenca'))

@app.route('/historico_geral')
@login_required
def historico_geral():
    periodo = request.args.get('periodo', 'mes')
    tipo = request.args.get('tipo', 'todos')
    pagamento = request.args.get('pagamento', 'todos')

    historico = listar_historico(periodo, tipo, pagamento)

    return render_template(
        'historico_geral.html',
        historico=historico,
        periodo=periodo,
        tipo=tipo,
        pagamento=pagamento
    )

@app.route('/historico_aluno/<int:id_aluno>')
@login_required
def historico_aluno(id_aluno):
    periodo = request.args.get('periodo', 'mes')
    tipo = request.args.get('tipo', 'todos')
    pagamento = request.args.get('pagamento', 'todos')
    data_aluno = listar_historico_aluno( id_aluno, periodo, tipo, pagamento )
    return render_template(
        'historico_aluno.html',
        data_aluno=data_aluno,
        periodo=periodo,
        tipo=tipo,
        pagamento=pagamento
    )

@app.route('/notificacoes')
@login_required
def notificacoes():
    alertas = listar_alertas()
    nao_lidas = contar_nao_lidas()

    return render_template(
        'notificacoes.html',
        alertas=alertas,
        nao_lidas=nao_lidas
    )

@app.route('/notificacoes/<int:id_alerta>/visualizar', methods=['PATCH'])
@login_required
def visualizar_notificacao(id_alerta):
    visualizar_alerta(id_alerta)
    return '', 204

@app.route('/usuarios')
@login_required
def usuarios():
    tipo_usuario = request.args.get('tipo', 'todos').lower()
    
    alunos=[{'id_aluno': a['id_aluno'], 'nome': a['nome'], 'tipo': 'Aluno'} for a in aluno_listar_todos()]
    usuarios=[ {'id_usuario': u['id_usuario'], 'nome': u['nome'], 'tipo': formatar_label(u['cargo']) } for u in usuario_listar_todos() if tipo_usuario == 'todos' or u['cargo'].lower() == tipo_usuario]

    if tipo_usuario == 'aluno':
        todos_usuarios = alunos
    elif tipo_usuario in ('administrador', 'estagiario'):
        todos_usuarios = usuarios
    else:
        todos_usuarios = alunos + usuarios
    return render_template('usuarios.html', todos_usuarios=todos_usuarios, tipo_usuario=tipo_usuario)

@app.route('/informacoes_usuario/<string:tipo>/<int:id>')
@login_required
def informacoes_usuario(tipo, id):
    registro=aluno_listar_por_id(id) if tipo.lower()=='aluno' else usuario_listar_por_id(id)
    return render_template('informacoes_usuario.html', nome=registro.get('nome'), tipo=tipo, id=id, registro=montar_registro(registro))

@app.route('/avaliacoes_usuario')
@login_required
def avaliacoes_usuario():
    avaliacoes = listar_avaliacoes()
    return render_template('avaliacoes_usuario.html',avaliacoes=avaliacoes)

@app.route('/avaliacoes_usuario/excluir/<int:id_avaliacao>', methods=['POST'])
@login_required
def excluir_avaliacao_rota(id_avaliacao):
    excluir_avaliacao(id_avaliacao)

    return redirect(url_for('avaliacoes_usuario'))

@app.route('/editar_usuario')
@login_required
def editar_usuario():
    return render_template('editar_usuario.html')