from datetime import datetime

## labels especiais são todas as que contêm acentos, hífen, ou formatações específicas
LABELS_ESPECIAIS={
    'INADIMPLENCIA': 'Inadimplência',
    'AUSENCIA': 'Ausência',
    'DISPONIVEL': 'Disponível',
    'cpf': 'CPF',
    'data_nascimento': 'D. Nascimento',
    'data_entrada': 'D. Matrícula',
    'id_usuario': None,
    'id_aluno': None,
    'senha_hash': None,
    'nome': None,
}

## limpezas simples
def formatar_label(label):
    return LABELS_ESPECIAIS.get(label, label.replace('_', ' ').title())

## formata data
def formatar_data_br(data):
    if not data:
        return None
    return datetime.strptime( data[:10], "%Y-%m-%d" ).strftime("%d/%m/%Y")

## converte o dict em uma lista formatada
def montar_registro(dicionario):
    registro=[]
    for coluna, info in dicionario.items():
        label=formatar_label(coluna)

        if label is None or info is None:
            continue

        if 'data' in coluna.lower() or coluna.endswith('_em'):
            info=formatar_data_br(info)
        elif isinstance(info, str):
            info=formatar_label(info)

        registro.append({'coluna': coluna, 'label': label, 'info': info})

    return registro