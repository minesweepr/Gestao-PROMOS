from app.database.supabase import supabase

def listar_presencas_por_periodo(inicio=None, fim=None, id_aluno=None):
    consulta = (
        supabase
        .table("presenca")
        .select("*")
        .order("data_presenca", desc=True)
    )
    if inicio:
        consulta = consulta.gte("data_presenca", inicio.isoformat())
    if fim:
        consulta = consulta.lt("data_presenca", fim.isoformat())
    if id_aluno:
        consulta = consulta.eq("id_aluno", id_aluno)

    return consulta.execute().data or []