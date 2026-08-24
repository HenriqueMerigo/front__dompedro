import re as regex
import requests as re
from datetime import date, datetime

porta = 5000
base = f"http://127.0.0.1:{porta}"



def edita_produto_servico(id_produto_servico, ds_produto_servico, ds_categoria, qt_estoque, vl_unitario_produto_compra, vl_unitario_produto_venda):
    url = f"{base}/edita_produto_servico/{id_produto_servico}"

    payload = {
        "id_produto_servico": id_produto_servico,
        "ds_produto_servico": ds_produto_servico,
        "ds_categoria": ds_categoria,
        "qt_estoque": qt_estoque,
        "vl_unitario_produto_compra": vl_unitario_produto_compra,
        "vl_unitario_produto_venda": vl_unitario_produto_venda
    }
    if not ds_produto_servico or not ds_categoria or not vl_unitario_produto_compra or not vl_unitario_produto_venda:
        raise ValueError("Todos os campos são obrigatórios e devem ser preenchidos corretamente.")

    response = re.put(url, json=payload)
    
    return response