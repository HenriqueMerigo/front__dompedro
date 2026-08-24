import requests as re
from datetime import date, datetime

porta = 5000
base = f"http://127.0.0.1:{porta}"


def insere_produto(nome, vl_unitario_produto_compra, estoque, vl_unitario_produto_venda):
    url = f"{base}/insere_produto"

    vl_prod_compra_str = (
        f"{float(vl_unitario_produto_compra):.2f}"
        if vl_unitario_produto_compra is not None
        else "0.00"
    )
    vl_prod_venda_str = (
        f"{float(vl_unitario_produto_venda):.2f}"
        if vl_unitario_produto_venda is not None
        else "0.00"
    )

    payload = {
        "ds_produto": nome,
        "qt_estoque": estoque,
        "vl_unitario_produto_compra": vl_prod_compra_str,
        "vl_unitario_produto_venda": vl_prod_venda_str,
    }

    response = re.post(url, json=payload)

    return response