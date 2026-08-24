import streamlit as st
import pandas as pd


from header.page_config import page_config

from endpoints.produto.insere_produto import insere_produto
from endpoints.produto.busca_produto import busca_produto
from endpoints.produto.edita_produto import edita_produto
from endpoints.produto.deleta_produto import deleta_produto

def produto():
    page_config()

    st.title("Produtos")

@st.dialog("Inserir Produto", width='large')
def modal_inserir_produto():
    st.write("Preencha os dados do novo produto:")

    col_descricao, col_estoque = st.columns(2)
    with col_descricao:
        nome = st.text_input("Descricao")
        vl_unitario_produto_compra = st.number_input("Valor de compra do produto")
    with col_estoque:
        estoque = st.number_input("Quantidade em Estoque", value=0, min_value=0)
        vl_unitario_produto_venda = st.number_input("Valor de venda do produto")


    if st.button("Salvar"):
        response = insere_produto(nome, vl_unitario_produto_compra, estoque, vl_unitario_produto_venda)
        if response.status_code != 201:
            st.error(f"Erro ao inserir produto: {response.text}")
        else:
            st.success(f"produto {nome} inserido com sucesso!")
            st.rerun()

@st.dialog("Editar Produto", width='large')
def modal_editar_produto():
    action = st.selectbox("Selecione o produto para editar", options=[f"{c['id_produto']} - {c['ds_produto']}" for c in busca_produto()])

    if action:
        id_produto = int(action.split(" - ")[0])
        produto_data = next((c for c in busca_produto() if c['id_produto'] == id_produto), None)

        if produto_data:
            st.write(f"Editando produto: {produto_data['ds_produto']}")

            col_nome, col_estoque = st.columns(2)
            with col_nome:
                nome = st.text_input("Nome", value=produto_data['ds_produto'])
                dh_prim_agenda = st.date_input("Data do primeiro agendamento", value=pd.to_datetime(produto_data['dh_primeiro_agendamento']))
            with col_estoque:
                estoque = st.text_input("Estoque", value=produto_data['ds_contato'])
                dh_ult_agenda = st.date_input("Data do último agendamento", value=pd.to_datetime(produto_data['dh_ultimo_agendamento']))

            if st.button("Salvar Alterações"):
                st.warning("Aguarde enquanto as alterações são salvas...")
                response = edita_produto(id_produto, nome, estoque, dh_prim_agenda, dh_ult_agenda)
                if response.status_code != 200:
                    st.error(f"Erro ao editar produto: {response.text}")
                else:
                    st.rerun()

@st.dialog("Deletar Produto", width="large")
def modal_deletar_produto():
    produtos = busca_produto()
    
    if not produtos:
        st.info("Nenhum produto encontrado.")
        return

    action = st.selectbox(
        "Selecione o produto para deletar",
        options=[f"{c['id_produto']} - {c['ds_produto']}" for c in produtos]
    )

    if action:
        id_produto = int(action.split(" - ")[0])

        if st.button("Deletar produto", use_container_width=True):
            st.session_state["confirmar_delete"] = True

        if st.session_state.get("confirmar_delete"):
            st.warning(f"Deseja realmente deletar o produto {action}?")
            
            if st.button("Confirmar Exclusão", use_container_width=True):
                response = deleta_produto(id_produto)
                
                if response.status_code == 200:
                    st.session_state["confirmar_delete"] = False
                    st.success("produto deletado com sucesso!")
                    st.rerun()
                else:
                    st.error(f"Erro ao deletar produto: {response.text}")


def modulo_todos():
    col_modulo_1, col_modulo_2, col_modulo_3 = st.columns([1, 1, 1])
    with col_modulo_1:
        if st.button("Inserir Produto", width='stretch'):
            modal_inserir_produto()

    with col_modulo_2:
        if st.button("Editar Produto", width='stretch'):
            modal_editar_produto()

    with col_modulo_3:
        if st.button("Deletar Produto", width='stretch'):
            modal_deletar_produto()

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