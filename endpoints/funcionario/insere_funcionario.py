import re as regex
import requests as re
from datetime import date, datetime

porta = 5000
base = f"http://127.0.0.1:{porta}"

def insere_funcionario(ds_funcionario, ds_contato, dh_primeiro_agendamento, dh_ultimo_agendamento, pe_comissao):
    url = f"{base}/insere_funcionario"

    # Trata as datas para garantir que fiquem no formato string (ISO)
    dh_prim_str = dh_primeiro_agendamento.isoformat() if isinstance(dh_primeiro_agendamento, (date, datetime)) else dh_primeiro_agendamento
    dh_ult_str = dh_ultimo_agendamento.isoformat() if isinstance(dh_ultimo_agendamento, (date, datetime)) else dh_ultimo_agendamento

    payload = {
        "ds_funcionario": ds_funcionario,
        "ds_contato": ds_contato,
        "dh_primeiro_agendamento": dh_prim_str,
        "dh_ultimo_agendamento": dh_ult_str,
        "pe_comissao": pe_comissao
    }
    if not ds_funcionario or not ds_contato or not dh_prim_str or not dh_ult_str:
        raise ValueError("Todos os campos são obrigatórios e devem ser preenchidos corretamente.")
    response = re.post(url, json=payload)
    
    return response