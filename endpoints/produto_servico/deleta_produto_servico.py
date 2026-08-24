import requests as re

porta = 5000
base = f"http://127.0.0.1:{porta}"

def deleta_produto_servico(id_produto_servico):
    if not id_produto_servico:
        raise ValueError("Selecione um cliente para deletar.")

    url = f"{base}/deleta_produto_servico/{id_produto_servico}"

    response = re.delete(url)
    
    return response