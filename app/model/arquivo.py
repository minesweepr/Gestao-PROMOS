from datetime import date
from uuid import uuid4
from werkzeug.utils import secure_filename
from app.database.supabase import supabase

BUCKET = "avaliacoes"
TAMANHO_MAXIMO = 5 * 1024 * 1024

def listar_avaliacoes(id_aluno=None):
    consulta = (
        supabase
        .table("avaliacao")
        .select("id_avaliacao, arquivo_pdf, data_avaliacao, aluno(nome)")
        .order("id_avaliacao", desc=True)
    )
    if id_aluno:
        consulta = consulta.eq("id_aluno", id_aluno)
    resposta = consulta.execute()
    avaliacoes = []
    for avaliacao in resposta.data or []:
        aluno = avaliacao.get("aluno") or {}
        avaliacoes.append({
            "id_avaliacao": avaliacao["id_avaliacao"],
            "nome": aluno.get("nome", "Aluno"),
            "arquivo_pdf": avaliacao.get("arquivo_pdf"),
            "nome_arquivo": avaliacao.get("arquivo_pdf", "").split("/")[-1].split("_", 1)[-1],
            "data_avaliacao": avaliacao.get("data_avaliacao")
        })

    return avaliacoes

def listar_alunos():
    resposta = (
        supabase
        .table("aluno")
        .select("id_aluno, nome")
        .eq("situacao", "ATIVO")
        .order("nome")
        .execute()
    )
    return resposta.data or []

def importar_avaliacao(arquivo, id_aluno, id_usuario):
    if not arquivo or not arquivo.filename:
        raise ValueError("Selecione um arquivo PDF.")
    if not id_aluno:
        raise ValueError("Selecione um aluno.")
    if not id_usuario:
        raise ValueError("Usuário não identificado.")
    id_aluno = int(id_aluno)
    if not arquivo.filename.lower().endswith(".pdf"):
        raise ValueError("Apenas arquivos PDF são permitidos.")
    arquivo.seek(0, 2)
    tamanho = arquivo.tell()
    arquivo.seek(0)
    if tamanho > TAMANHO_MAXIMO:
        raise ValueError("O arquivo deve ter no máximo 5 MB.")
    nome = secure_filename(arquivo.filename)
    caminho = f"{id_aluno}/{uuid4()}_{nome}"
    conteudo = arquivo.read()
    supabase.storage.from_(BUCKET).upload( caminho, conteudo, { "content-type": "application/pdf", "upsert": False } )

    try:
        resposta = (
            supabase
            .table("avaliacao")
            .insert({ "id_aluno": id_aluno, "id_usuario": id_usuario, "data_avaliacao": date.today().isoformat(), "arquivo_pdf": caminho })
            .execute()
        )
        return resposta.data
    except Exception:
        supabase.storage.from_(BUCKET).remove([caminho])
        raise

def excluir_avaliacao(id_avaliacao):
    resposta = ( supabase .table("avaliacao") .select("arquivo_pdf") .eq("id_avaliacao", id_avaliacao) .single() .execute() )
    arquivo_pdf = resposta.data.get("arquivo_pdf")
    if arquivo_pdf:
        supabase.storage.from_(BUCKET).remove([arquivo_pdf])
    resposta = ( supabase .table("avaliacao") .delete() .eq("id_avaliacao", id_avaliacao) .execute() )
    return resposta.data

def obter_avaliacao_pdf(id_avaliacao):
    avaliacao = ( supabase .table("avaliacao") .select("arquivo_pdf") .eq("id_avaliacao", id_avaliacao) .single() .execute() )
    return supabase.storage.from_(BUCKET).download( avaliacao.data["arquivo_pdf"] )