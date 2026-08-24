import re as regex
import requests as re
from datetime import date, datetime

porta = 5000
base = f"http://127.0.0.1:{porta}"



def edita_produto(id_cliente, nome, telefone, dh_prim_agenda, dh_ult_agenda):
    url = f"{base}/edita_cliente/{id_cliente}"

    # Trata as datas para garantir que fiquem no formato string (ISO)
    dh_prim_str = dh_prim_agenda.isoformat() if isinstance(dh_prim_agenda, (date, datetime)) else dh_prim_agenda
    dh_ult_str = dh_ult_agenda.isoformat() if isinstance(dh_ult_agenda, (date, datetime)) else dh_ult_agenda

    payload = {
        "ds_cliente": nome,
        "ds_contato": telefone,
        "dh_primeiro_agendamento": dh_prim_str,
        "dh_ultimo_agendamento": dh_ult_str
    }
    if not nome or not telefone or not dh_prim_str or not dh_ult_str:
        raise ValueError("Todos os campos são obrigatórios e devem ser preenchidos corretamente.")

    response = re.put(url, json=payload)
    
    return response