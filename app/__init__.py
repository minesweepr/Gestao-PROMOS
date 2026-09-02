import os
from flask import Flask, session
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "chave_secreta_padrao")

@app.context_processor
def inject_user():
    return {
        "usuario_logado": {
            "nome": session.get("usuario_nome"),
            "cargo": session.get("usuario_cargo"),
            "is_admin": session.get("usuario_cargo") == "ADMINISTRADOR",
            "is_personal": session.get("usuario_cargo") in ["ADMINISTRADOR", "PERSONAL"]
        }
    }

from app import routes
from app.auth import auth

app.register_blueprint(auth)