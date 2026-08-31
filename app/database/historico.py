from datetime import date, datetime, timedelta
from app.database.supabase import supabase

def voltar_meses(data, meses):
    mes = data.month - meses
    ano = data.year
    while mes <= 0:
        mes += 12
        ano -= 1
    return date(ano, mes, 1)

def obter_periodo(periodo):
    hoje = date.today()
    fim = hoje + timedelta(days=1)
    periodos = {
        "semana": hoje - timedelta(days=hoje.weekday()),
        "mes": hoje.replace(day=1),
        "3meses": voltar_meses(hoje, 2),
        "6meses": voltar_meses(hoje, 5)
    }
    return periodos.get(periodo), fim

def formatar_data_br(data):
    if not data:
        return None
    return datetime.strptime( data[:10], "%Y-%m-%d" ).strftime("%d/%m/%Y")

def buscar_presencas(inicio, fim, id_aluno=None):
    consulta = (
        supabase
        .table("presenca")
        .select( "id_presenca, data_presenca, id_aluno, " "aluno(id_aluno, nome)" )
        .lt("data_presenca", fim.isoformat())
        .order("data_presenca", desc=True)
    )
    if inicio:
        consulta = consulta.gte( "data_presenca", inicio.isoformat() )
    if id_aluno:
        consulta = consulta.eq("id_aluno", id_aluno)
    return consulta.execute().data or []

def buscar_pagamentos(inicio, fim, pagamento="todos", id_aluno=None):
    consulta = (
        supabase
        .table("pagamento")
        .select( "id_pagamento, id_aluno, valor, " "data_pagamento, status, " "aluno(id_aluno, nome)" )
        .lt("data_pagamento", fim.isoformat())
        .order("data_pagamento", desc=True)
    )
    if inicio:
        consulta = consulta.gte( "data_pagamento", inicio.isoformat() )
    if pagamento in ("pago", "pendente"):
        consulta = consulta.eq( "status", "PAGO" if pagamento == "pago" else "PENDENTE" )
    if id_aluno:
        consulta = consulta.eq("id_aluno", id_aluno)
    return consulta.execute().data or []


def montar_historico(presencas, pagamentos, tipo):
    historico = {}
    if tipo in ("todos", "presencas"):
        for registro in presencas:
            aluno = registro.get("aluno")
            if not aluno:
                continue

            data = registro["data_presenca"][:10]
            id_aluno = aluno["id_aluno"]

            registro_historico = {
                "id_aluno": id_aluno,
                "nome": aluno["nome"],
                "id_presenca": registro["id_presenca"],
                "tipo": "presenca",
                "presente": True,
                "pagamento": None,
                "status_pagamento": None,
                "id_pagamento": None
            }

            if tipo == "presencas":
                historico.setdefault(data, []).append( registro_historico )
            else:
                historico.setdefault(data, {})[id_aluno] = ( registro_historico )

    if tipo in ("todos", "pagamentos"):
        for registro in pagamentos:
            aluno = registro.get("aluno")
            if not aluno:
                continue

            data = registro["data_pagamento"][:10]
            id_aluno = aluno["id_aluno"]
            registro_historico = {
                "id_aluno": id_aluno,
                "nome": aluno["nome"],
                "id_presenca": None,
                "tipo": "pagamento",
                "presente": False,
                "pagamento": registro["valor"],
                "status_pagamento": registro["status"],
                "id_pagamento": registro["id_pagamento"]
            }

            if tipo == "pagamentos":
                historico.setdefault(data, []).append( registro_historico )
            else:
                dia = historico.setdefault(data, {})

                if id_aluno in dia:
                    dia[id_aluno].update({
                        "pagamento": registro["valor"],
                        "status_pagamento": registro["status"],
                        "id_pagamento": registro["id_pagamento"]
                    })
                else:
                    dia[id_aluno] = registro_historico

    if tipo in ("presencas", "pagamentos"):
        resultado = [ { "data": formatar_data_br(data), "alunos": alunos } for data, alunos in historico.items() ]
    else:
        resultado = [ { "data": formatar_data_br(data), "alunos": list(alunos.values()) } for data, alunos in historico.items() ]

    resultado.sort( key=lambda dia: datetime.strptime( dia["data"], "%d/%m/%Y" ), reverse=True )

    return resultado


def listar_historico( periodo=None, tipo="todos", pagamento="todos" ):
    inicio, fim = obter_periodo(periodo)
    presencas = []
    pagamentos = []
    if tipo in ("todos", "presencas"):
        presencas = buscar_presencas(inicio, fim)
    if tipo in ("todos", "pagamentos"):
        pagamentos = buscar_pagamentos( inicio, fim, pagamento )
    return montar_historico( presencas, pagamentos, tipo )

def listar_historico_aluno( id_aluno, periodo=None, tipo="todos", pagamento="todos" ):
    inicio, fim = obter_periodo(periodo)
    presencas = ( buscar_presencas(inicio, fim, id_aluno) if tipo in ("todos", "presencas") else [] )
    pagamentos = ( buscar_pagamentos(inicio, fim, pagamento, id_aluno) if tipo in ("todos", "pagamentos") else [] )
    aluno = next( (r["aluno"] for r in presencas + pagamentos if r.get("aluno")), None )
    historico = {}

    def obter_registro(data):
        return historico.setdefault(data, { "data": formatar_data_br(data), "presente": False, "pagamento": None })
    
    for registro in presencas:
        data = registro["data_presenca"][:10]
        obter_registro(data)["presente"] = True
    for registro in pagamentos:
        data = registro["data_pagamento"][:10]
        obter_registro(data)["pagamento"] = { "valor": registro["valor"], "status": registro["status"] }
    historico = [ historico[data] for data in sorted(historico, reverse=True) ]

    return {
        "aluno": aluno,
        "historico": historico,
        "ultima_presenca": ( formatar_data_br(presencas[0]["data_presenca"]) if presencas else None ),
        "saldo_devedor": sum( r["valor"] for r in pagamentos if r["status"] == "PENDENTE" )
    }