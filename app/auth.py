from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session
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

            return redirect(url_for("presenca"))

        except Exception as erro:
            print("Erro de autenticação no Supabase:", erro)
            return render_template(
                "login.html",
                erro="E-mail ou senha inválidos."
            )

    return render_template("login.html")


@auth.route("/logout")
def logout():
    try:
        supabase.auth.sign_out()
    except Exception as erro:
        print("Erro ao sair no Supabase:", erro)

    session.clear()
    return redirect(url_for("auth.login"))