import streamlit as st
import pandas as pd
import time


from header.page_config import page_config

from endpoints.produto_servico.insere_produto_servico import insere_produto_servico
from endpoints.produto_servico.busca_produto_servico import busca_produto_servico
from endpoints.produto_servico.edita_produto_servico import edita_produto_servico
from endpoints.produto_servico.deleta_produto_servico import deleta_produto_servico

def produto():
    page_config()

    st.title("Produtos")


@st.dialog("Inserir Produto Servico", width='large')
def modal_inserir_produto_servico():
    st.write("Preencha os dados do novo produto:")

    ds_produto_servico = st.text_input("Descricao")
    col_descricao, col_estoque = st.columns(2)
    with col_descricao:
        ds_categoria = st.selectbox("Categoria", ("Produto", "Servico"))
        vl_unitario_produto_compra = st.number_input("Valor de compra do produto/servico")
    with col_estoque:
        qt_estoque = st.number_input("Quantidade em Estoque", value=0, min_value=0)
        vl_unitario_produto_venda = st.number_input("Valor de venda do produto/servico")

    if st.button("Salvar"):
        response = insere_produto_servico(ds_produto_servico, ds_categoria, qt_estoque, vl_unitario_produto_compra, vl_unitario_produto_venda)
        if response.status_code != 201:
            st.error(f"Erro ao inserir produto: {response.text}")
        else:
            st.success(f"O {ds_categoria} foi inserido com sucesso!")
            time.sleep(2)
            st.rerun()

@st.dialog("Editar Produto Servico", width='large')
def modal_editar_produto_servico():
    action = st.selectbox("Selecione o produto para editar", options=[f"{c['id_produto_servico']} - {c['ds_produto_servico']}" for c in busca_produto_servico()])

    if action:
        id_produto_servico = int(action.split(" - ")[0])
        produto_servico_data = next((c for c in busca_produto_servico() if c['id_produto_servico'] == id_produto_servico), None)

        if produto_servico_data:
            st.write(f"Editando produto/servico: {produto_servico_data['ds_produto_servico']}")

            ds_produto_servico = st.text_input("Descricao", value=produto_servico_data['ds_produto_servico'])
            col_nome, col_telefone = st.columns(2)
            with col_nome:
                ds_categoria = st.selectbox("Categoria", ("Produto", "Servico"))
                vl_unitario_produto_compra = st.number_input("Valor de compra do produto/servico", value=produto_servico_data['vl_unitario_produto_compra'])
            with col_telefone:
                qt_estoque = st.number_input("Quantidade em Estoque", value=int(produto_servico_data['qt_estoque']), min_value=0)
                vl_unitario_produto_venda = st.number_input("Valor de venda do produto/servico", value=produto_servico_data['vl_unitario_produto_venda'])

            if st.button("Salvar Alterações"):
                st.warning("Aguarde enquanto as alterações são salvas...")
                time.sleep(2)
                response = edita_produto_servico(id_produto_servico, ds_produto_servico, ds_categoria, qt_estoque, vl_unitario_produto_compra, vl_unitario_produto_venda)
                if response.status_code != 200:
                    st.error(f"Erro ao editar cliente: {response.text}")
                else:
                    st.rerun()

@st.dialog("Deletar Produto", width="large")
def modal_deletar_produto_servico():
    produtos = busca_produto_servico()
    
    if not produtos:
        st.info("Nenhum produto encontrado.")
        return

    action = st.selectbox(
        "Selecione o produto para deletar",
        options=[f"{c['id_produto_servico']} - {c['ds_produto_servico']}" for c in produtos]
    )

    if action:
        id_produto_servico = int(action.split(" - ")[0])
        st.session_state["confirmar_delete"] = False
        if st.button("Deletar produto", width='stretch'):
            response = deleta_produto_servico(id_produto_servico)
            
            if response.status_code == 200:
                time.sleep(2)
                st.success("produto deletado com sucesso!")
                st.rerun()
            else:
                st.error(f"Erro ao deletar produto: {response.text}")




def modulo_todos():
    col_modulo_1, col_modulo_2, col_modulo_3 = st.columns([1, 1, 1])
    with col_modulo_1:
        if st.button("Inserir Produto/Servico", width='stretch'):
            modal_inserir_produto_servico()

    with col_modulo_2:
        if st.button("Editar Produto/Servico", width='stretch'):
            modal_editar_produto_servico()

    with col_modulo_3:
        if st.button("Deletar Produto/Servico", width='stretch'):
            modal_deletar_produto_servico()


if __name__ == "__main__":
    produto()
    option_map = { 
        0: "Todos",
        1: "Servicos",
        2: "Produtos"
    }
    selection = st.pills(
        "Selecione a secao que deseja acessar:",
        options=option_map.keys(),
        format_func=lambda option: option_map[option],
        selection_mode="single",
    )

    if selection == 0 or selection == None:
        modulo_todos()

        dados = busca_produto_servico()
        if dados:
            df = pd.DataFrame(dados)
    
            colunas_ordem = [
                "id_produto_servico",
                "ds_produto_servico",
                "ds_categoria",
                "qt_estoque",
                "vl_unitario_produto_compra",
                "vl_unitario_produto_venda",
                "dh_ultima_movimentacao"
            ]
            df = df[colunas_ordem]
    
            df = df.rename(columns={
                "id_produto_servico": "Código",
                "ds_produto_servico": "Descricao do Produto/Servico",
                "ds_categoria": "Categoria",
                "qt_estoque": "Estoque",
                "vl_unitario_produto_compra": "Valor de Compra",
                "vl_unitario_produto_venda": "Valor de Venda",
                "dh_ultima_movimentacao": "Ultima Venda"
            })
    
            st.dataframe(df, hide_index=True, width="content")