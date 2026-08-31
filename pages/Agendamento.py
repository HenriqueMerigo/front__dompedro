import calendar
from datetime import date, datetime
import time
import requests
import streamlit as st

from endpoints.agendamento.busca_agendamento import busca_agendamento, busca_agendamento_front
from endpoints.agendamento.deleta_agendamento import deleta_agendamento
from endpoints.agendamento.edita_agendamento import edita_agendamento
from endpoints.agendamento.insere_agendamento import insere_agendamento, insere_agendamento_produto_servico
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

@st.dialog("Inserir Agendamento", width="large")
def modal_inserir_agendamento():
    st.write("Preencha os dados do novo agendamento:")

    dados_funcionario = busca_funcionario() or []
    dados_cliente = busca_cliente() or []

    # 1. Campos de Identificação
    col_1, col_2 = st.columns(2)
    with col_1:
        funcionario_obj = st.selectbox(
            "Funcionario:", 
            options=dados_funcionario,
            format_func=lambda x: x.get('ds_funcionario', '') if isinstance(x, dict) else str(x)
        )
        dia_agendamento = st.date_input("Data do Agendamento:")
    with col_2:
        cliente_obj = st.selectbox(
            "Cliente:", 
            options=dados_cliente,
            format_func=lambda x: x.get('ds_cliente', '') if isinstance(x, dict) else str(x)
        )
        horario_agendamento = st.time_input("Horário Início:")

    st.divider()

    # 2. Seleção de Categoria e Itens
    col_opcao, col_item = st.columns(2)

    with col_opcao:
        option = st.selectbox("Categoria", ("Produto", "Servico"))

    if option == "Produto":
        dados_produto_servico = busca_produto() or []
        label_select = "Selecione o Produto"
    else:
        dados_produto_servico = busca_servico() or []
        label_select = "Selecione o Servico"

    lista_opcoes = [item['ds_produto_servico'] for item in dados_produto_servico if isinstance(item, dict) and 'ds_produto_servico' in item]

    with col_item:
        produto_servico = st.selectbox(label_select, options=lista_opcoes)

    # 3. Inserção no session_state recuperando o ID e preço
    if st.button("Inserir Produto / Servico", width='stretch'):
        if produto_servico:
            item_encontrado = next(
                (item for item in dados_produto_servico if isinstance(item, dict) and item.get('ds_produto_servico') == produto_servico), 
                None
            )
            
            if item_encontrado:
                # Busca dinâmica por qualquer variação do campo ID retornado pela API
                id_prod = None
                for chave, valor in item_encontrado.items():
                    if chave.startswith('id_') or chave.startswith('cd_') or chave == 'id':
                        id_prod = valor
                        break
                
                preco = (
                    item_encontrado.get('vl_unitario_produto_venda') or 
                    item_encontrado.get('vl_unitario_servico') or 
                    item_encontrado.get('vl_produto') or 
                    item_encontrado.get('vl_servico') or 
                    0.0
                )

                st.session_state.itens_selecionados.append({
                    "id_produto_servico": id_prod,
                    "Descrição": produto_servico,
                    "qt_produto": 1,
                    "Preço Unitário": float(preco)
                })

    # 4. Exibição dos itens
    st.write("### Itens Adicionados")
    
    if not st.session_state.itens_selecionados:
        df_exibicao = {
            "id_produto_servico": [],
            "Descrição": [],
            "qt_produto": [],
            "Preço Unitário": []
        }
    else:
        df_exibicao = st.session_state.itens_selecionados

    st.dataframe(df_exibicao, width='stretch')

    col_1, col_2, col_3 = st.columns(3)

    with col_1:
        vl_desconto_agendamento = st.number_input("Valor de Desconto Previo:", min_value=0.0)

    with col_2:
        vl_gorjeta_agendamento = st.number_input("Valor de Gorjeta Previa:", min_value=0.0)

    vl_total_bruto_agendamento = sum(item["Preço Unitário"] for item in st.session_state.itens_selecionados)
    vl_total_liquido_agendamento = vl_total_bruto_agendamento - vl_desconto_agendamento + vl_gorjeta_agendamento
    with col_3:
        st.metric("Valor Total", f"R$ {vl_total_liquido_agendamento:,.2f}")
    
    if st.button("Limpar Lista de Produtos/Servicos"):
        st.session_state.itens_selecionados = []

    st.divider()

    dh_agendamento = f"{dia_agendamento} {horario_agendamento}"

    id_funcionario = funcionario_obj.get('id_funcionario') if isinstance(funcionario_obj, dict) else None
    id_cliente = cliente_obj.get('id_cliente') if isinstance(cliente_obj, dict) else None

    if st.button("Inserir agendamento", use_container_width=True):
        if id_cliente is None or id_funcionario is None:
            st.error("Selecione um Cliente e um Funcionário válidos!")
        elif not st.session_state.itens_selecionados:
            st.error("Adicione pelo menos um produto ou serviço ao agendamento!")
        else:
            st.warning("Aguarde enquanto o agendamento é inserido...")
            
            # 1. Insere o Agendamento Principal
            response = insere_agendamento(
                id_cliente, 
                id_funcionario, 
                vl_total_bruto_agendamento, 
                vl_desconto_agendamento, 
                vl_gorjeta_agendamento,
                vl_total_liquido_agendamento, 
                dh_agendamento
            )
            
            if response.status_code != 201:
                st.error(f"Erro ao inserir agendamento: {response.text}")
                time.sleep(2)
            else:
                # 2. Iteração com tratamento de erro
                sucesso_itens = True
                for item in st.session_state.itens_selecionados:
                    id_prod_serv = item.get("id_produto_servico")
                    
                    if id_prod_serv is None:
                        st.error(f"Erro: O ID do item '{item.get('Descrição')}' está nulo!")
                        sucesso_itens = False
                        continue

                    quantidade = item.get("qt_produto", 1)
                    vl_unitario = item.get("Preço Unitário", 0.0)
                    vl_total = vl_unitario * quantidade

                    resp_item = insere_agendamento_produto_servico(
                        id_produto_servico=int(id_prod_serv),
                        qt_produto=int(quantidade),
                        vl_unitario_produto=float(vl_unitario),
                        vl_total_produto=float(vl_total)
                    )

                    if resp_item.status_code != 201:
                        sucesso_itens = False
                        st.error(f"Erro ao vincular item '{item.get('Descrição')}': {resp_item.text}")

                if sucesso_itens:
                    st.success("Agendamento e itens inseridos com sucesso!")
                    st.session_state.itens_selecionados = []
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

    agendamento_selecionado = st.selectbox(
        "Selecione o agendamento para deletar",
        options=lista_agendamentos,
        format_func=lambda c: f"ID Agendamento {c.get('id_agendamento')} - Funcionario {c.get('id_funcionario')} - Cliente {c.get('id_cliente')} - {c.get('dh_agendamento')} - R$ {c.get('vl_total_liquido_agendamento')}",
    )

    if agendamento_selecionado:
        id_agendamento = int(agendamento_selecionado.get("id_agendamento"))
        confirmar = st.checkbox("Tenho certeza de que desejo excluir este agendamento")

        if st.button(
            "Deletar agendamento",
            type="primary",
            width='stretch',
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
        if st.button("Agendar Novo", width='stretch'):
            st.session_state.itens_selecionados = []
            modal_inserir_agendamento()
            
    with col_editar:
        st.button("Editar Agendamento", width='stretch')
        
    with col_remover:
        if st.button("Remover Agendamento", width='stretch'):
            modal_deletar_agendamento()










@st.dialog("Detalhes da Data", width="large")
def abrir_modal_data(data):
    data_formatada = data.strftime("%d/%m/%Y")
    data_api = data.strftime("%Y-%m-%d")

    st.write(f"Você selecionou o dia **{data_formatada}**.")

    resultado = busca_agendamento_front(data_api)

    if resultado:
        agora = datetime.now()

        # Converte a string de data/hora em datetime para calcular a diferença absoluta de tempo
        def obter_diferenca_tempo(item):
            # Tenta converter com hora/minuto/segundo ou apenas data se vier truncado
            try:
                dh_item = datetime.strptime(item["dh_agendamento"], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                dh_item = datetime.strptime(item["dh_agendamento"], "%Y-%m-%d %H:%M")
            
            return abs(dh_item - agora)

        # Ordena a lista: do menor intervalo para o maior em relação ao horário atual
        agendamentos_ordenados = sorted(resultado, key=obter_diferenca_tempo)

        # Renderiza um st.metric por agendamento, empilhados verticalmente
        for item in agendamentos_ordenados:
            # Formatação opcional para exibir a hora no rótulo
            try:
                hora_str = datetime.strptime(item["dh_agendamento"], "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
            except ValueError:
                hora_str = item["dh_agendamento"]

            st.metric(
                label=f"⏰ Horário: {hora_str} | Cliente: {item['ds_cliente']} (Profissional: {item['ds_funcionario']})",
                value=f"R$ {item['vl_total_liquido_agendamento']:.2f}",
                border=True
            )
            editar, deletar = st.columns(2)
            with editar:
                if st.button(f"Editar agendamento do cliente {item['ds_cliente']} - {hora_str}", width='stretch'):
                    st.write("nada ainda")
            with deletar:
                if st.button(f"Deletar agendamento do cliente {item['ds_cliente']} - {hora_str}", width='stretch'):
                    st.write("nada ainda")

    elif resultado == []:
        st.warning("Nenhum agendamento marcado para esta data.")

    else:
        st.error("Erro ao buscar dados do servidor. Verifique a conexão com a API.")
















def calendario():
    hoje = date.today()

    col_mes, col_ano = st.columns([2, 1])
    with col_mes:
        meses = [
            "Janeiro",
            "Fevereiro",
            "Março",
            "Abril",
            "Maio",
            "Junho",
            "Julho",
            "Agosto",
            "Setembro",
            "Outubro",
            "Novembro",
            "Dezembro",
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
                    label_dia = (
                        f"📆 {dia}" if data_atual_btn == hoje else str(dia)
                    )

                    if st.button(
                        label=label_dia,
                        key=f"btn_data_{ano}_{mes_num}_{dia}",
                        use_container_width=True,
                    ):
                        # 2. Ao clicar, atualiza o estado e dispara o modal
                        st.session_state["data_selecionada"] = data_atual_btn
                        abrir_modal_data(data_atual_btn)

    if "data_selecionada" in st.session_state:
        data_f = st.session_state["data_selecionada"].strftime("%d/%m/%Y")
        st.success(f"Última data confirmada: **{data_f}**")

def agendamento():
    page_config()
    st.title("Agendamento")
    st.caption("Selecione um dia no calendário para visualizar os horários.")

    interacoes()
    calendario()

if __name__ == "__main__":
    agendamento()