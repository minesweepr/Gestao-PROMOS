from app.database.supabase import supabase

def listar_pagamentos(inicio=None, fim=None, status=None, id_aluno=None):
    consulta = (
        supabase
        .table("pagamento")
        .select("*")
        .order("data_pagamento", desc=True)
    )
    if inicio:
        consulta = consulta.gte("data_pagamento", inicio.isoformat())
    if fim:
        consulta = consulta.lt("data_pagamento", fim.isoformat())
    if status:
        consulta = consulta.eq("status", status)
    if id_aluno:
        consulta = consulta.eq("id_aluno", id_aluno)

    return consulta.execute().data or []