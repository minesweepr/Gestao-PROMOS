from app.database.supabase import supabase

COLUNAS="id_usuario, nome, cpf, email, cargo, status, criado_em"

def usuario_listar_todos():
    resposta=(
        supabase
        .table("usuario").select(COLUNAS)
        .order("nome")
        .execute()
    )
    return resposta.data or []

def usuario_listar_por_id(id_usuario):
    resposta=(
        supabase
        .table("usuario")
        .select(COLUNAS)
        .eq("id_usuario", id_usuario)
        .maybe_single()
        .execute()
    )
    return resposta.data