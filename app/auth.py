from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from app.database.supabase import supabase

auth = Blueprint("auth", __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function

@auth.route("/", methods=["GET", "POST"])
def login():
    if "usuario_id" in session:
        return redirect(url_for("presenca"))

    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        try:
            resposta = supabase.auth.sign_in_with_password({
                "email": email,
                "password": senha
            })

            session["usuario_id"] = resposta.user.id
            session["access_token"] = resposta.session.access_token

            res_usuario = supabase.table('usuario').select("id_usuario", "nome", "cargo").eq('auth_user_id', resposta.user.id).execute()

            if res_usuario.data:
                session["id_usuario"] = res_usuario.data[0].get("id_usuario")
                session["usuario_nome"] = res_usuario.data[0].get("nome")
                session["usuario_cargo"] = res_usuario.data[0].get("cargo")
            else:
                session["usuario_nome"] = resposta.user.user_metadata.get("nome", "Usuário")
                session["usuario_cargo"] = resposta.user.user_metadata.get("cargo", "ESTAGIARIO")

            return redirect(url_for("presenca"))

        except Exception as erro:
            print("Erro de autenticação no Supabase:", erro)
            return render_template("login.html", erro="E-mail ou senha inválidos.")

    return render_template("login.html")

@auth.route("/logout")
def logout():
    try:
        supabase.auth.sign_out()
    except Exception as erro:
        print("Erro ao sair no Supabase:", erro)

    session.clear()
    return redirect(url_for("auth.login"))

@auth.route("/esqueci_senha", methods=["GET", "POST"])
def esqueci_senha():
    if request.method == "POST":
        email = request.form.get("email")

        try:
            supabase.auth.reset_password_for_email(
                email,
                {"redirect_to": request.host_url.rstrip('/') + url_for('auth.redefinir_senha')}
            )
            return render_template("esqueci_senha.html", sucesso="E-mail de recuperação enviado! Verifique sua caixa de entrada.")
        except Exception as erro:
            print("Erro ao solicitar recuperação:", erro)
            return render_template("esqueci_senha.html", erro="Erro ao enviar e-mail. Verifique o endereço digitado.")

    return render_template("esqueci_senha.html")

@auth.route("/redefinir_senha", methods=["GET", "POST"])
def redefinir_senha():
    if request.method == "POST":
        try:
            data = request.get_json(force=True, silent=True) or {}
            access_token = data.get("access_token")
            refresh_token = data.get("refresh_token")
            nova_senha = data.get("senha")

            if not nova_senha or len(nova_senha) < 6:
                return jsonify({"sucesso": False, "mensagem": "A senha deve conter no mínimo 6 caracteres."}), 400

            if not access_token:
                return jsonify({"sucesso": False, "mensagem": "Sessão inválida ou o link de recuperação expirou. Solicite um novo e-mail."}), 401

            supabase.auth.set_session(access_token, refresh_token or "")
            supabase.auth.update_user({"password": nova_senha})
            supabase.auth.sign_out()

            return jsonify({"sucesso": True, "redirect_url": url_for("auth.login")})

        except Exception as erro:
            print("Erro ao redefinir senha no Supabase:", erro)
            msg_erro = str(erro)

            if "same_password" in msg_erro or "should be different" in msg_erro:
                msg_erro = "A nova senha não pode ser igual à senha anterior."
            else:
                msg_erro = "Erro ao atualizar a senha. O link pode ter expirado."

            return jsonify({"sucesso": False, "mensagem": msg_erro}), 400

    return render_template("redefinir_senha.html")