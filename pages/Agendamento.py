import calendar
from datetime import date, datetime
import time
import requests
import streamlit as st

from endpoints.agendamento.busca_agendamento import busca_agendamento
from endpoints.agendamento.deleta_agendamento import deleta_agendamento
from endpoints.agendamento.edita_agendamento import edita_agendamento
from endpoints.agendamento.insere_agendamento import insere_agendamento
from endpoints.produto_servico.busca_produto_servico import (
    busca_produto,
    busca_servico,
)
from endpoints.funcionario.busca_funcionario import busca_funcionario
from endpoints.cliente.busca_cliente import busca_cliente

from header.navigation import navigation
from header.page_config import hide_sidebar, page_config

if "itens_selecionados" not in st.session_state:
    st.session_state["itens_selecionados"] = []
st.session_state.itens_selecionados = []

@st.dialog("Inserir Agendamento", width="large")
def modal_inserir_agendamento():
    st.write("Preencha os dados do novo agendamento:")

    dados_funcionario = busca_funcionario()
    lista_funcionario = [item_funcionario['ds_funcionario'] for item_funcionario in dados_funcionario if isinstance(item_funcionario, dict)]
    dados_cliente = busca_cliente()
    lista_cliente = [item_cliente['ds_cliente'] for item_cliente in dados_cliente if isinstance(item_cliente, dict)]

    # 1. Campos de Identificação
    col_1, col_2 = st.columns(2)
    with col_1:
        funcionario = st.selectbox("Funcionario:", options=lista_funcionario)
        dia_agendamento = st.date_input("Data do Agendamento:")
    with col_2:
        cliente = st.selectbox("Cliente:", options=lista_cliente)
        horario_agendamento = st.time_input("Horário Início:")

    st.divider()


    # Selectboxes em 2 colunas lado a lado
    col_opcao, col_item = st.columns(2)

    with col_opcao:
        option = st.selectbox("Categoria", ("Produto", "Servico"))

    # Busca os dados conforme a opção escolhida
    if option == "Produto":
        dados_produto_servico = busca_produto()
        label_select = "Selecione o Produto"
    else:
        dados_produto_servico = busca_servico()
        label_select = "Selecione o Servico"

    lista_opcoes = [item_produto['ds_produto_servico'] for item_produto in dados_produto_servico if isinstance(item_produto, dict)]

    with col_item:
        produto_servico = st.selectbox(label_select, options=lista_opcoes)

    # 3. Inserção no session_state recuperando o preço correto
    if st.button("Inserir Produto / Servico", use_container_width=True):
        if produto_servico:
            item_encontrado = next(
                (item for item in dados_produto_servico if isinstance(item, dict) and item.get('ds_produto_servico') == produto_servico), 
                None
            )
            
            preco = item_encontrado.get('vl_unitario_produto_venda', 0.0) if item_encontrado else 0.0

            st.session_state.itens_selecionados.append({
                "Descrição": produto_servico,
                "Preço Unitário": preco
            })

    # 4. Exibição da tabela/dataframe fixa (mesmo vazia)
    st.write("### Itens Adicionados")
    
    # Se a lista estiver vazia, cria a estrutura com colunas para exibir o cabeçalho
    if not st.session_state.itens_selecionados:
        df_exibicao = {
            "Descrição": [],
            "Preço Unitário": []
        }
    else:
        df_exibicao = st.session_state.itens_selecionados

    st.dataframe(df_exibicao, use_container_width=True)


    col_1, col_2, col_3 = st.columns(3)

    with col_1:
        vl_desconto_agendamento = st.number_input("Valor de Desconto Previo:")

    with col_2:
        vl_gorjeta_agendamento = st.number_input("Valor de Gorjeta Previa:")

    vl_total_bruto_agendamento = sum(item["Preço Unitário"] for item in st.session_state.itens_selecionados)
    vl_total_liquido_agendamento = vl_total_bruto_agendamento - vl_desconto_agendamento + vl_gorjeta_agendamento
    with col_3:
        st.metric("Valor Total", f"R$ {vl_total_liquido_agendamento:,.2f}")
    
    if st.button("Limpar Lista de Produtos/Servicos"):
        st.session_state.itens_selecionados = []

    st.divider()

    dh_agendamento = str(dia_agendamento) + ' ' + str(horario_agendamento)

    dados_funcionario_id = busca_funcionario()
    ids_funcionario = [
        item['id_funcionario'] 
        for item in dados_funcionario_id 
        if isinstance(item, dict) and 'id_funcionario' in item
    ]
    id_funcionario = int(ids_funcionario[0]) if ids_funcionario else None

    dados_cliente_id = busca_cliente()
    ids_cliente = [
        item['id_cliente'] 
        for item in dados_cliente_id 
        if isinstance(item, dict) and 'id_cliente' in item
    ]
    id_cliente = int(ids_cliente[0]) if ids_cliente else None

    if st.button("Inserir agendamento", use_container_width=True):
        # Validação para garantir que os IDs são válidos antes de enviar
        if id_cliente is None or id_funcionario is None:
            st.error("Selecione um Cliente e um Funcionário válidos!")
        else:
            st.warning("Aguarde enquanto o agendamento é inserido...")
            
            response = insere_agendamento(
                id_cliente, 
                id_funcionario, 
                vl_total_bruto_agendamento, 
                vl_desconto_agendamento, 
                vl_gorjeta_agendamento, 
                vl_total_liquido_agendamento, 
                dh_agendamento
            )
            
            time.sleep(2)
            if response.status_code != 201:
                st.error(f"Erro ao inserir agendamento: {response.text}")
                time.sleep(2)
            else:
                st.success("Agendamento inserido com sucesso!")
                time.sleep(2)
                st.rerun()

@st.dialog("Deletar Agendamento", width="large")
def modal_deletar_agendamento():
    agendamento_busca = busca_agendamento()

    if not agendamento_busca:
        st.info("Nenhum agendamento encontrado.")
        return

    lista_agendamentos = [
        item for item in agendamento_busca if isinstance(item, dict)
    ]

    if not lista_agendamentos:
        st.info("Nenhum agendamento válido encontrado.")
        return

    # O selectbox guarda o dicionário completo, mas exibe o texto amigável via format_func
    agendamento_selecionado = st.selectbox(
        "Selecione o agendamento para deletar",
        options=lista_agendamentos,
        format_func=lambda c: f"ID Agendamento {c.get('id_agendamento')} - Funcionario {c.get('id_funcionario')} - Cliente {c.get('id_cliente')} - {c.get('dh_agendamento')} - R$ {c.get('vl_total_liquido_agendamento')}",
    )

    if agendamento_selecionado:
        # Pega o ID diretamente como inteiro
        id_agendamento = int(agendamento_selecionado.get("id_agendamento"))

        # Controle simples de estado de confirmação usando checkbox/toggle
        confirmar = st.checkbox("Tenho certeza de que desejo excluir este agendamento")

        if st.button(
            "Deletar agendamento",
            type="primary",
            use_container_width=True,
            disabled=not confirmar,
        ):
            response = deleta_agendamento(id_agendamento)

            if response.status_code == 200:
                st.session_state["confirmar_delete"] = False
                st.success("Agendamento deletado com sucesso!")
                time.sleep(2)
                st.rerun()
            else:
                st.error(f"Erro ao deletar agendamento: {response.text}")

def interacoes():
    col_novo, col_editar, col_remover = st.columns(3)

    with col_novo:
        if st.button("Agendar Novo", use_container_width=True):
            modal_inserir_agendamento()
    with col_editar:
        st.button("Editar Agendamento", use_container_width=True)
    with col_remover:
        if st.button("Remover Agendamento", use_container_width=True):
            modal_deletar_agendamento()



def calendario():
    hoje = date.today()

    col_mes, col_ano = st.columns([2, 1])
    with col_mes:
        meses = [
            "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
        ]
        mes_nome = st.selectbox("Mês", meses, index=hoje.month - 1)
        mes_num = meses.index(mes_nome) + 1

    with col_ano:
        ano = st.number_input(
            "Ano", min_value=2024, max_value=2030, value=hoje.year
        )

    calendar.setfirstweekday(calendar.SUNDAY)
    matriz_mes = calendar.monthcalendar(ano, mes_num)

    st.markdown("---")

    dias_semana = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
    cols_header = st.columns(7)
    for idx, col in enumerate(cols_header):
        col.markdown(f"**{dias_semana[idx]}**")

    for semana in matriz_mes:
        cols = st.columns(7)
        for i in range(7):
            dia = semana[i]
            with cols[i]:
                if dia == 0:
                    st.write("")
                else:
                    data_atual_btn = date(ano, mes_num, dia)
                    foi_passado = data_atual_btn < hoje
                    label_dia = (
                        f"📆 {dia}" if data_atual_btn == hoje else str(dia)
                    )

                    if st.button(
                        label=label_dia,
                        key=f"btn_data_{ano}_{mes_num}_{dia}",
                        disabled=foi_passado,
                        use_container_width=True,
                    ):
                        st.session_state["data_selecionada"] = data_atual_btn

    if "data_selecionada" in st.session_state:
        data_f = st.session_state["data_selecionada"].strftime("%d/%m/%Y")
        st.success(f"Data selecionada: **{data_f}**")


def agendamento():
    page_config()
    st.title("Agendamento")
    st.caption("Selecione um dia no calendário para visualizar os horários.")

    interacoes()
    calendario()


if __name__ == "__main__":
    agendamento()