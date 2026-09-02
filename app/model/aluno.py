from app.database.supabase import supabase

COLUNAS='id_aluno, nome, cpf, telefone, email, data_nascimento, data_entrada, tipo_aluno, situacao, criado_em'

def aluno_listar_todos(situacao=None):
    tabela=supabase.table("aluno").select(COLUNAS)
    if situacao:
        tabela=tabela.eq("situacao", situacao)

    resposta=(
        tabela
        .order("nome")
        .execute()
    )
    return resposta.data or []

def aluno_listar_por_id(id_aluno):
    resposta=(
        supabase
        .table("aluno")
        .select(COLUNAS)
        .eq("id_aluno", id_aluno)
        .maybe_single()
        .execute()
    )
    return resposta.data