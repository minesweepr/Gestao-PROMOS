from app.database.supabase import supabase

def listar_avaliacoes():
    resposta = (
        supabase
        .table("avaliacao")
        .select("id_avaliacao, nome")
        .order("id_avaliacao", desc=True)
        .execute()
    )

    return resposta.data or []


def excluir_avaliacao(id_avaliacao):
    resposta = (
        supabase
        .table("avaliacao")
        .delete()
        .eq("id_avaliacao", id_avaliacao)
        .execute()
    )

    return resposta.data

