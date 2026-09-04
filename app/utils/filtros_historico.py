from datetime import date, timedelta

from app.model.presenca import listar_presencas_por_periodo
from app.model.pagamento import listar_pagamentos

def obter_periodo(periodo):
    hoje = date.today()
    inicio = {
        "semana": hoje - timedelta(days=hoje.weekday()),
        "mes": hoje.replace(day=1),
        "3meses": hoje.replace(day=1) - timedelta(days=60),
        "6meses": hoje.replace(day=1) - timedelta(days=150),
    }.get(periodo)
    if periodo in ("3meses", "6meses"):
        inicio = inicio.replace(day=1)
    return inicio, hoje + timedelta(days=1)

def _status(pagamento):
    return { "pago": "PAGO", "pendente": "PENDENTE", }.get(pagamento)

def filtrar_historico(periodo=None, tipo="todos", pagamento="todos"):
    inicio, fim = obter_periodo(periodo)
    presencas = ( listar_presencas_por_periodo(inicio, fim) if tipo in ("todos", "presencas") else [] )
    pagamentos = ( listar_pagamentos(inicio, fim, _status(pagamento)) if tipo in ("todos", "pagamentos") else [] )
    return presencas, pagamentos

def filtrar_historico_aluno( id_aluno, periodo=None, tipo="todos", pagamento="todos" ):
    inicio, fim = obter_periodo(periodo)
    presencas = ( listar_presencas_por_periodo(inicio, fim, id_aluno) if tipo in ("todos", "presencas") else [] )
    pagamentos = ( listar_pagamentos(inicio, fim, _status(pagamento), id_aluno) if tipo in ("todos", "pagamentos") else [] )
    return presencas, pagamentos