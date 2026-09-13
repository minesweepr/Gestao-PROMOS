from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session ,jsonify, redirect, url_for
from app.database.supabase import supabase


auth = Blueprint("auth", __name__)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


@auth.route("/login", methods=["GET", "POST"])
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

            # Busca os dados do perfil (cargo e nome) do usuário logado
            res_usuario = supabase.table('usuario').select("id_usuario","nome, cargo").eq('auth_user_id', resposta.user.id).execute()
            
            if res_usuario.data:
                session["id_usuario"] = res_usuario.data[0].get("id_usuario")
                session["usuario_nome"] = res_usuario.data[0].get("nome")
                session["usuario_cargo"] = res_usuario.data[0].get("cargo") # ADMINISTRADOR ou ESTAGIARIO
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

# 1. Rota para solicitar o envio do e-mail de recuperação
@auth.route("/esqueci_senha", methods=["GET", "POST"])
def esqueci_senha():
    if request.method == "POST":
        email = request.form.get("email")
        
        try:
            # Envia o e-mail pelo Supabase redirecionando de volta para a sua rota de redefinição
            supabase.auth.reset_password_for_email(
                email, 
                {"redirect_to": request.host_url + "redefinir_senha"}
            )
            return render_template("esqueci_senha.html", sucesso="E-mail de recuperação enviado! Verifique sua caixa de entrada.")
        except Exception as erro:
            print("Erro ao solicitar recuperação:", erro)
            return render_template("esqueci_senha.html", erro="Erro ao enviar e-mail. Verifique o endereço digitado.")

    return render_template("esqueci_senha.html")


@auth.route("/redefinir_senha", methods=["GET"])
def redefinir_senha():
    return render_template("redefinir_senha.html")