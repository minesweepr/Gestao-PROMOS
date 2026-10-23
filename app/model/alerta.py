from app.database.supabase import supabase

def listar_alertas():
    resposta = (
        supabase
        .table("alerta")
        .select("*, aluno!alerta_id_aluno_fkey(nome)")
        .order("status", desc=False)
        .order("data_alerta", desc=True)
        .execute()
    )

    alertas = resposta.data or []

    for alerta in alertas:
        aluno = alerta.get("aluno")
        nome_aluno = aluno.get("nome") if aluno else None
        descricao = alerta.get("descricao") or ""

        alerta["descricao_exibida"] = (
            f"{nome_aluno} - {descricao}"
            if nome_aluno
            else descricao
        )

    return alertas

def contar_nao_lidas():
    resposta = (
        supabase
        .table("alerta")
        .select("id_alerta", count="exact")
        .eq("status", "PENDENTE")
        .execute()
    )
    return resposta.count or 0

def atualizar_status_alerta(id_alerta, status):
    return (
        supabase.table('alerta')
        .update({'status': status})
        .eq('id_alerta', id_alerta)
        .execute()
    )