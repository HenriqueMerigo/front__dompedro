import re as regex
import requests as re
from datetime import date, datetime

porta = 5000
base = f"http://127.0.0.1:{porta}"

def insere_agendamento(id_cliente, id_funcionario, vl_total_bruto_agendamento, vl_desconto_agendamento, vl_gorjeta, vl_total_liquido_agendamento, dh_agendamento):
    url = f"{base}/insere_agendamento"

    # Trata as datas para garantir que fiquem no formato string (ISO)
    dh_agenda = dh_agendamento.isoformat() if isinstance(dh_agendamento, (date, datetime)) else dh_agendamento
    
    payload = {
        "id_cliente": id_cliente,
        "id_funcionario": id_funcionario,
        "vl_total_bruto_agendamento": vl_total_bruto_agendamento,
        "vl_desconto_agendamento": vl_desconto_agendamento,
        "vl_gorjeta": vl_gorjeta,
        "vl_total_liquido_agendamento": vl_total_liquido_agendamento,
        "dh_agendamento": dh_agenda
    }
    if not id_cliente or not id_funcionario or not dh_agendamento:
        raise ValueError("Todos os campos são obrigatórios e devem ser preenchidos corretamente.")

    response = re.post(url, json=payload)
    
    return response

def insere_agendamento_produto_servico(id_produto_servico, qt_produto, vl_unitario_produto, vl_total_produto):
    url = f"{base}/insere_agendamento_produto_servico"
    
    payload = {
        "id_produto_servico" : str(id_produto_servico),
        "qt_produto" : qt_produto,
        "vl_unitario_produto" : vl_unitario_produto,
        "vl_total_produto" : vl_total_produto
    }
    if not id_produto_servico:
        raise ValueError("Os produtos/servicos são obrigatórios e devem ser preenchidos corretamente.")
    print(payload)
    response = re.post(url, json=payload)
    
    return response