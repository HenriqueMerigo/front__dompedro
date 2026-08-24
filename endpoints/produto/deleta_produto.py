import requests as re

porta = 5000
base = f"http://127.0.0.1:{porta}"

def deleta_produto(id_cliente):
    if not id_cliente:
        raise ValueError("Selecione um cliente para deletar.")

    url = f"{base}/deleta_cliente/{id_cliente}"

    response = re.delete(url)
    
    return response