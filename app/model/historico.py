from app.model.aluno import aluno_listar_todos, aluno_listar_por_id
from app.model.pagamento import listar_pagamentos_aluno
from app.model.presenca import listar_ultima_presenca
from app.utils.formatadores import formatar_data_br
from app.utils.filtros_historico import filtrar_historico

def listar_historico(periodo=None, tipo=None, pagamento=None):
    presencas, pagamentos = filtrar_historico( periodo, tipo, pagamento )
    alunos = {a["id_aluno"]: a["nome"] for a in aluno_listar_todos("ATIVO")}
    historico = {}
    for p in presencas:
        data = p["data_presenca"][:10]
        item = {
            "id_aluno": p["id_aluno"],
            "nome": alunos.get(p["id_aluno"]),
            "id_presenca": p["id_presenca"],
            "tipo": "presenca",
            "presente": True,
        }
        if tipo == "presencas":
            historico.setdefault(data, []).append(item)
        else:
            historico.setdefault(data, {})[p["id_aluno"]] = item

    for p in pagamentos:
        data = p["data_pagamento"][:10]
        id_aluno = p["id_aluno"]
        item = {
            "id_aluno": id_aluno,
            "nome": alunos.get(id_aluno),
            "id_pagamento": p["id_pagamento"],
            "tipo": "pagamento",
            "pagamento": p["valor"],
            "status_pagamento": p["status"],
        }
        if tipo == "pagamentos":
            historico.setdefault(data, []).append(item)
        elif id_aluno in historico.setdefault(data, {}):
            historico[data][id_aluno].update(item)
        else:
            historico[data][id_aluno] = item

    return [
        { "data": formatar_data_br(data), "alunos": list(registros.values()) if tipo is None else registros, }
        for data, registros in sorted(historico.items(), reverse=True)
    ]   

def listar_historico_aluno(id_aluno, periodo=None, tipo=None, pagamento=None):
    presencas, pagamentos = filtrar_historico( periodo=periodo, tipo=tipo, pagamento=pagamento, id_aluno=id_aluno )
    aluno = aluno_listar_por_id(id_aluno)
    ultima_presenca = listar_ultima_presenca(id_aluno)
    pagamentos_aluno = listar_pagamentos_aluno(id_aluno)
    datas = {}
    for p in presencas:
        data = p["data_presenca"][:10]
        datas.setdefault(data, {"presente": False, "pagamento": None})
        datas[data]["presente"] = True
    for p in pagamentos:
        data = p["data_pagamento"][:10]
        datas.setdefault(data, {"presente": False, "pagamento": None})
        datas[data]["pagamento"] = { "valor": p["valor"], "status": p["status"] }
    return {
        "aluno": aluno,
        "historico": [ { "data": formatar_data_br(data), **info } for data, info in sorted(datas.items(), reverse=True) ],
        "ultima_presenca": ( formatar_data_br(ultima_presenca["data_presenca"]) if ultima_presenca else None ),
        "saldo_devedor": sum( p["valor"] for p in pagamentos_aluno if p["status"] == "CANCELADO" )
    }