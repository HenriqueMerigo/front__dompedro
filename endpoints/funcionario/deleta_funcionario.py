import requests as re

porta = 5000
base = f"http://127.0.0.1:{porta}"

def deleta_funcionario(id_funcionario):
    if not id_funcionario:
        raise ValueError("Selecione um funcionario para deletar.")

    url = f"{base}/deleta_funcionario/{id_funcionario}"

    response = re.delete(url)
    
    return response