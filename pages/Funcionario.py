import streamlit as st
import pandas as pd
import time


from header.page_config import page_config

from endpoints.funcionario.insere_funcionario import insere_funcionario
from endpoints.funcionario.busca_funcionario import busca_funcionario
from endpoints.funcionario.edita_funcionario import edita_funcionario
from endpoints.funcionario.deleta_funcionario import deleta_funcionario

def funcionario():
    page_config()

    st.title("Funcionarios")
    st.caption("Esta é a página de funcionarios.")

@st.dialog("Inserir funcionario", width='large')
def modal_inserir_funcionario():
    st.write("Preencha os dados do novo funcionario:")

    ds_funcionario = st.text_input("Nome do funcionario:")
    col_nome, col_telefone = st.columns(2)
    with col_nome:
        pe_comissao = st.number_input("Porcentagem de comissao:", value=0, min_value=0)
        dh_primeiro_agendamento = st.date_input("Data do primeiro agendamento:")
    with col_telefone:
        ds_contato = st.text_input("Telefone:")
        dh_ultimo_agendamento = st.date_input("Data do último agendamento:")


    if st.button("Salvar"):
        response = insere_funcionario(ds_funcionario, ds_contato, dh_primeiro_agendamento, dh_ultimo_agendamento, pe_comissao)
        if response.status_code != 201:
            st.error(f"Erro ao inserir funcionario: {response.text}")
        else:
            st.success(f"funcionario {ds_funcionario} inserido com sucesso!")
            time.sleep(2)
            st.rerun()

@st.dialog("Editar funcionario", width='large')
def modal_editar_funcionario():
    action = st.selectbox("Selecione o funcionario para editar", options=[f"{c['id_funcionario']} - {c['ds_funcionario']}" for c in busca_funcionario()])

    if action:
        id_funcionario = int(action.split(" - ")[0])
        funcionario_data = next((c for c in busca_funcionario() if c['id_funcionario'] == id_funcionario), None)

        if funcionario_data:
            st.write(f"Editando funcionario: {funcionario_data['ds_funcionario']}")

            ds_funcionario = st.text_input("Nome", value=funcionario_data['ds_funcionario'])
            col_nome, col_telefone = st.columns(2)
            with col_nome:
                pe_comissao = st.number_input("Porcentagem de comissao:", value=0, min_value=0)
                dh_primeiro_agendamento = st.date_input("Data do primeiro agendamento", value=pd.to_datetime(funcionario_data['dh_primeiro_agendamento']))
            with col_telefone:
                ds_contato = st.text_input("Telefone", value=funcionario_data['ds_contato'])
                dh_ultimo_agendamento = st.date_input("Data do último agendamento", value=pd.to_datetime(funcionario_data['dh_ultimo_agendamento']))

            if st.button("Salvar Alterações"):
                st.warning("Aguarde enquanto as alterações são salvas...")
                time.sleep(2)
                response = edita_funcionario(id_funcionario, ds_funcionario, ds_contato, dh_primeiro_agendamento, dh_ultimo_agendamento, pe_comissao)
                if response.status_code != 200:
                    st.error(f"Erro ao editar funcionario: {response.text}")
                    time.sleep(2)
                else:
                    st.rerun()

@st.dialog("Deletar funcionario", width="large")
def modal_deletar_funcionario():
    funcionarios = busca_funcionario()
    
    if not funcionarios:
        st.info("Nenhum funcionario encontrado.")
        return

    action = st.selectbox(
        "Selecione o funcionario para deletar",
        options=[f"{c['id_funcionario']} - {c['ds_funcionario']}" for c in funcionarios]
    )

    if action:
        id_funcionario = int(action.split(" - ")[0])

        if st.button("Deletar funcionario", use_container_width=True):
            st.session_state["confirmar_delete"] = True

        if st.session_state.get("confirmar_delete"):
            st.warning(f"Deseja realmente deletar o funcionario {action}?")
            
            if st.button("Confirmar Exclusão", use_container_width=True):
                response = deleta_funcionario(id_funcionario)
                
                if response.status_code == 200:
                    st.session_state["confirmar_delete"] = False
                    st.success("funcionario deletado com sucesso!")
                    st.rerun()
                else:
                    st.error(f"Erro ao deletar funcionario: {response.text}")

if __name__ == "__main__":
    funcionario()

    col_modulo_1, col_modulo_2, col_modulo_3 = st.columns([1, 1, 1])
    with col_modulo_1:
        if st.button("Inserir funcionario", width='stretch'):
            modal_inserir_funcionario()
                            
    with col_modulo_2:
        if st.button("Editar funcionario", width='stretch'):
            modal_editar_funcionario()

    with col_modulo_3:
        if st.button("Deletar funcionario", width='stretch'):
            modal_deletar_funcionario()

    dados = busca_funcionario()
    if dados:
        df = pd.DataFrame(dados)

        colunas_ordem = [
            "id_funcionario",
            "ds_funcionario",
            "ds_contato",
            "dh_primeiro_agendamento",
            "dh_ultimo_agendamento",
            "pe_comissao"
        ]
        df = df[colunas_ordem]

        df = df.rename(columns={
            "id_funcionario": "Codigo",
            "ds_funcionario": "Nome",
            "ds_contato": "Telefone",
            "dh_primeiro_agendamento": "Primeiro Agendamento",
            "dh_ultimo_agendamento": "Ultimo Agendamento",
            "pe_comissao": "% Comissao"
        })

        st.dataframe(df, hide_index=True)