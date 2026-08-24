import streamlit as st
import pandas as pd


from header.page_config import page_config

from endpoints.cliente.insere_cliente import insere_cliente
from endpoints.cliente.busca_cliente import busca_cliente
from endpoints.cliente.edita_cliente import edita_cliente
from endpoints.cliente.deleta_cliente import deleta_cliente

def cliente():
    page_config()

    st.title("Clientes")
    st.write("Esta é a página de clientes.")

@st.dialog("Inserir Cliente", width='large')
def modal_inserir_cliente():
    st.write("Preencha os dados do novo cliente:")

    col_nome, col_telefone = st.columns(2)
    with col_nome:
        nome = st.text_input("Nome")
        dh_prim_agenda = st.date_input("Data do primeiro agendamento")
    with col_telefone:
        telefone = st.text_input("Telefone")
        dh_ult_agenda = st.date_input("Data do último agendamento")


    if st.button("Salvar"):
        response = insere_cliente(nome, telefone, dh_prim_agenda, dh_ult_agenda)
        if response.status_code != 201:
            st.error(f"Erro ao inserir cliente: {response.text}")
        else:
            st.success(f"Cliente {nome} inserido com sucesso!")
            st.rerun()

@st.dialog("Editar Cliente", width='large')
def modal_editar_cliente():
    action = st.selectbox("Selecione o cliente para editar", options=[f"{c['id_cliente']} - {c['ds_cliente']}" for c in busca_cliente()])

    if action:
        id_cliente = int(action.split(" - ")[0])
        cliente_data = next((c for c in busca_cliente() if c['id_cliente'] == id_cliente), None)

        if cliente_data:
            st.write(f"Editando cliente: {cliente_data['ds_cliente']}")

            col_nome, col_telefone = st.columns(2)
            with col_nome:
                nome = st.text_input("Nome", value=cliente_data['ds_cliente'])
                dh_prim_agenda = st.date_input("Data do primeiro agendamento", value=pd.to_datetime(cliente_data['dh_primeiro_agendamento']))
            with col_telefone:
                telefone = st.text_input("Telefone", value=cliente_data['ds_contato'])
                dh_ult_agenda = st.date_input("Data do último agendamento", value=pd.to_datetime(cliente_data['dh_ultimo_agendamento']))

            if st.button("Salvar Alterações"):
                st.warning("Aguarde enquanto as alterações são salvas...")
                response = edita_cliente(id_cliente, nome, telefone, dh_prim_agenda, dh_ult_agenda)
                if response.status_code != 200:
                    st.error(f"Erro ao editar cliente: {response.text}")
                else:
                    st.rerun()

@st.dialog("Deletar Cliente", width="large")
def modal_deletar_cliente():
    clientes = busca_cliente()
    
    if not clientes:
        st.info("Nenhum cliente encontrado.")
        return

    action = st.selectbox(
        "Selecione o cliente para deletar",
        options=[f"{c['id_cliente']} - {c['ds_cliente']}" for c in clientes]
    )

    if action:
        id_cliente = int(action.split(" - ")[0])

        if st.button("Deletar Cliente", use_container_width=True):
            st.session_state["confirmar_delete"] = True

        if st.session_state.get("confirmar_delete"):
            st.warning(f"Deseja realmente deletar o cliente {action}?")
            
            if st.button("Confirmar Exclusão", use_container_width=True):
                response = deleta_cliente(id_cliente)
                
                if response.status_code == 200:
                    st.session_state["confirmar_delete"] = False
                    st.success("Cliente deletado com sucesso!")
                    st.rerun()
                else:
                    st.error(f"Erro ao deletar cliente: {response.text}")

if __name__ == "__main__":
    cliente()

    col_modulo_1, col_modulo_2, col_modulo_3 = st.columns([1, 1, 1])
    with col_modulo_1:
        if st.button("Inserir Cliente", width='stretch'):
            modal_inserir_cliente()
                            
    with col_modulo_2:
        if st.button("Editar Cliente", width='stretch'):
            modal_editar_cliente()

    with col_modulo_3:
        if st.button("Deletar Cliente", width='stretch'):
            modal_deletar_cliente()

    dados = busca_cliente()
    if dados:
        df = pd.DataFrame(dados)

        colunas_ordem = [
            "id_cliente",
            "ds_cliente",
            "ds_contato",
            "dh_primeiro_agendamento",
            "dh_ultimo_agendamento",
            "dh_inclusao"
        ]
        df = df[colunas_ordem]

        df = df.rename(columns={
            "id_cliente": "Código",
            "ds_cliente": "Nome do Cliente",
            "ds_contato": "Telefone / Contato",
            "dh_primeiro_agendamento": "1º Agendamento",
            "dh_ultimo_agendamento": "Último Agendamento",
            "dh_inclusao": "Criado Em"
        })

        st.dataframe(df, hide_index=True)