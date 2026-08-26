import requests as re

porta = 5000
base = f"http://127.0.0.1:{porta}"

def deleta_agendamento(id_agendamento):
    if not id_agendamento:
        raise ValueError("Selecione um agendamento para deletar.")

    url = f"{base}/deleta_agendamento/{id_agendamento}"

    response = re.delete(url)
    
    return response