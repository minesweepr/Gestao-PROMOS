import os
from datetime import timedelta # <-- ADICIONAR ESTA IMPORTAÇÃO
from flask import Flask, session
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "chave_secreta_padrao")

# --- ADICIONAR ESTAS LINHAS PARA MANTER A SESSÃO ATIVA ---
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

app.config["SUPABASE_URL"] = os.getenv("SUPABASE_URL")
app.config["SUPABASE_PUBLISHABLE_KEY"] = os.getenv("SUPABASE_PUBLISHABLE_KEY")

@app.before_request
def make_session_permanent():
    session.permanent = True
# ---------------------------------------------------------

@app.context_processor
def inject_user():
    return {
        "usuario_logado": {
            "nome": session.get("usuario_nome"),
            "cargo": session.get("usuario_cargo"),
            "is_admin": session.get("usuario_cargo") == "ADMINISTRADOR",
            "is_estagiario": session.get("usuario_cargo") in ["ADMINISTRADOR", "ESTAGIARIO"]
        }
    }

from app import routes
from app.auth import auth

app.register_blueprint(auth)