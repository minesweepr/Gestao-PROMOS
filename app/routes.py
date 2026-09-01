from datetime import date
from flask import render_template, request, jsonify
from app import app
from app.auth import login_required
from app.database.supabase import supabase, supabase_admin

@app.route('/cadastrar_usuario', methods=['GET', 'POST'])
@login_required
def cadastrar_usuario():
    if request.method == 'POST':
        perfil = request.form.get('perfil')
        nome = request.form.get('nome')
        cpf = request.form.get('cpf')

        if not cpf or len(cpf) != 11 or not cpf.isdigit():
            return jsonify({"sucesso": False, "mensagem": "O CPF deve conter exatamente 11 números."}), 400

        try:
            # 1. CADASTRO DE USUÁRIO DO SISTEMA (ADMINISTRADOR / PERSONAL)
            if perfil in ['ADMINISTRADOR', 'PERSONAL']:
                email = request.form.get('email')
                senha = request.form.get('senha')

                if not senha or len(senha) < 6:
                    return jsonify({"sucesso": False, "mensagem": "A senha deve ter no mínimo 6 caracteres."}), 400

                # Criar conta no Auth
                res_auth = supabase_admin.auth.admin.create_user({
                    "email": email,
                    "password": senha,
                    "email_confirm": True,
                    "user_metadata": {"nome": nome, "cargo": perfil, "cpf": cpf}
                })

                auth_user_id = res_auth.user.id if res_auth and res_auth.user else None

                # Inserção manual e explícita na tabela public.usuario
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
    return render_template('presenca.html')


@app.route('/historico_geral')
@login_required
def historico_geral():
    return render_template('historico_geral.html')


@app.route('/historico_aluno')
@login_required
def historico_aluno():
    return render_template('historico_aluno.html')


@app.route('/notificacoes')
@login_required
def notificacoes():
    return render_template('notificacoes.html')


@app.route('/planilhas')
@login_required
def planilhas():
    return render_template('planilhas.html')


@app.route('/usuarios')
@login_required
def usuarios():
    return render_template('usuarios.html')


@app.route('/informacoes_usuario')
@login_required
def informacoes_usuario():
    return render_template('informacoes_usuario.html')


@app.route('/avaliacoes_usuario')
@login_required
def avaliacoes_usuario():
    return render_template('avaliacoes_usuario.html')


@app.route('/editar_usuario')
@login_required
def editar_usuario():
    return render_template('editar_usuario.html')