from datetime import date, datetime, timedelta
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

def listar_presencas_hoje():
    inicio, fim=_dia_min_max()
    resposta=(
        supabase
        .table("presenca")
        .select("id_aluno")
        .gte("data_presenca", inicio)
        .lt("data_presenca", fim)
        .execute()
    )
    return resposta.data or []

def presenca_aluno_marcar(id_aluno, id_usuario):
    resposta=(
        supabase
        .table("presenca")
        .insert({
            "id_aluno": id_aluno, 
            "id_usuario": id_usuario,
        })
        .execute()
    )
    return resposta.data

def presenca_aluno_desmarcar(id_aluno):
    inicio, fim=_dia_min_max()
    resposta=(
        supabase
        .table("presenca")
        .delete()
        .eq("id_aluno", id_aluno)
        .gte("data_presenca", inicio)
        .lt("data_presenca", fim)
        .execute()
    )
    return resposta.data

# função(ões) interna(s)
## função para achar o inicio e fim do dia
def _dia_min_max():
    inicio=datetime.combine(date.today(), datetime.min.time())
    fim=inicio+timedelta(days=1)
    return inicio.isoformat(), fim.isoformat()