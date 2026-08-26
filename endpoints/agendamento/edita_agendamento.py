import re as regex
import requests as re
from datetime import date, datetime

porta = 5000
base = f"http://127.0.0.1:{porta}"

def edita_agendamento(id_cliente, id_funcionario, vl_total_bruto_agendamento, vl_desconto_agendamento, vl_gorjeta, vl_total_liquido_agendamento, dh_agendamento):
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