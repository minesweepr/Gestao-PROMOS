from app.database.supabase import supabase

def listar_alertas():
    resposta = (
        supabase
        .table("alerta")
        .select("*")
        .order("status", desc=False)
        .order("data_alerta", desc=True)
        .execute()
    )

    return resposta.data or []


def contar_nao_lidas():
    resposta = (
        supabase
        .table("alerta")
        .select("id_alerta", count="exact")
        .eq("status", "PENDENTE")
        .execute()
    )

    return resposta.count or 0

def visualizar_alerta(id_alerta):
    (
        supabase
        .table("alerta")
        .update({"status": "VISUALIZADO"})
        .eq("id_alerta", id_alerta)
        .execute()
    )