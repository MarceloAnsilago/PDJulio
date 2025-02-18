import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu  # Biblioteca para menu estilizado

from database import (
    criar_banco_de_dados,
    buscar_usuario_bd,
    cadastrar_usuario_bd,
    listar_usuarios_bd,
    excluir_usuario_bd,
    atualizar_usuario_bd,
    cadastrar_produto_bd,
    listar_produtos_bd,
    atualizar_produto_bd,
    cadastrar_movimentacao,
    listar_movimentacoes_bd,
    criar_tabela_movimentos,
    excluir_produto_bd
)

################################################
#  PÁGINAS
################################################

def pagina_cadastrar_produtos():
    st.title("Gerenciar Produtos")

    # Cria duas abas
    tab1, tab2 = st.tabs(["Cadastrar/Editar Produtos", "Entrada de Produtos"])

    ################################################
    # Aba 1: Cadastrar/Editar Produtos
    ################################################
    with tab1:
        st.subheader("Cadastrar Novo Produto")
        with st.form("cadastro_novo_produto"):
            nome = st.text_input("Nome do Produto")
            preco = st.number_input("Preço de Venda", min_value=0.0, format="%.2f")
            info = st.text_area("Informações Complementares")
            status = st.selectbox("Status", ["Ativo", "Inativo"])

            if st.form_submit_button("Cadastrar"):
                produto_id = cadastrar_produto_bd(nome, info, status, preco)
                if produto_id:
                    st.success(f"Produto '{nome}' cadastrado com sucesso! (ID={produto_id})")
                else:
                    st.error(f"Erro ao cadastrar o produto '{nome}'.")

        st.write("---")
        st.subheader("Lista de Produtos Cadastrados")

        produtos = listar_produtos_bd()
        if not produtos:
            st.info("Nenhum produto cadastrado ainda.")
            return

        # listar_produtos_bd() => (id, nome, info, status, preco)
        df = pd.DataFrame(produtos, columns=["ID", "Nome", "Info", "Status", "Preço"])
        st.dataframe(df, use_container_width=True)

        # Seletor para editar
        opcoes = [f"{p[0]} - {p[1]}" for p in produtos]
        escolha = st.selectbox("Selecione um produto:", opcoes)
        if escolha:
            produto_id = int(escolha.split(" - ")[0])
            produto_info = next((p for p in produtos if p[0] == produto_id), None)
            if produto_info:
                pid, pnome, pinfo, pstatus, ppreco = produto_info
                st.write(f"**Editando produto:** {pnome} (ID={pid})")

                with st.form("editar_produto"):
                    novo_nome = st.text_input("Nome do Produto", value=pnome)
                    novo_preco = st.number_input("Preço de Venda", value=ppreco, min_value=0.0, format="%.2f")
                    nova_info = st.text_area("Informações Complementares", value=pinfo)
                    novo_status = st.selectbox(
                        "Status",
                        ["Ativo", "Inativo"],
                        index=0 if pstatus == "Ativo" else 1
                    )
                    if st.form_submit_button("Alterar"):
                        atualizar_produto_bd(pid, novo_nome, nova_info, novo_status, novo_preco)
                        st.success(f"Produto '{novo_nome}' atualizado com sucesso!")
                        st.rerun()

    ################################################
    # Aba 2: Entrada de Produtos
    ################################################
    with tab2:
        def pagina_entrada_produtos():
            st.title("Entrada de Produtos")

            # Filtra os produtos ativos
            produtos_todos = listar_produtos_bd()
            produtos_ativos = [p for p in produtos_todos if p[3] == "Ativo"]  # p[3] => status

            if produtos_ativos:
                df = pd.DataFrame(produtos_ativos, columns=["ID", "Nome", "Info", "Status", "Preço"])
                st.dataframe(df, use_container_width=True)

                # Combobox para selecionar produto
                opcoes = [f"{p[0]} - {p[1]}" for p in produtos_ativos]
                escolha = st.selectbox("Selecione um produto para entrada:", opcoes)

                if escolha:
                    produto_id = int(escolha.split(" - ")[0])
                    produto_info = next((p for p in produtos_ativos if p[0] == produto_id), None)
                    if produto_info:
                        st.write(f"Produto selecionado: {escolha}")
                        # p => (id, nome, info, status, preco)
                        # Vamos buscar as movimentações para calcular o saldo
                        movimentos = listar_movimentacoes_bd()

                        # Calcular entradas
                        entradas = sum(
                            m[6] for m in movimentos
                            if m[3] == produto_info[1]  # m[3] => nome do produto
                               and m[7].lower() == "entrada"
                               and m[10].lower() == "ativo"
                        )
                        # Calcular saídas
                        saidas = sum(
                            m[6] for m in movimentos
                            if m[3] == produto_info[1]
                               and m[7].lower() in ("saída", "saida", "venda")
                               and m[10].lower() == "ativo"
                        )
                        saldo_atual = entradas - saidas

                        with st.form("form_entrada_produto"):
                            # Campos
                            quantidade_nova = st.number_input("Quantidade a Registrar", min_value=1, step=1)
                            custo_inicial = st.number_input("Custo Inicial (por unidade)", min_value=0.0, format="%.2f")
                            preco_venda = st.number_input(
                                "Preço de Venda (por unidade)",
                                min_value=0.0,
                                value=produto_info[4],
                                disabled=True,
                                format="%.2f"
                            )
                            st.number_input("Saldo Atual", value=float(saldo_atual), disabled=True, format="%.0f")
                            metodo_pagamento = st.selectbox("Método de Pagamento", ["Dinheiro", "Cartão", "Cheque", "Outro"])

                            if st.form_submit_button("Registrar Entrada"):
                                usuario = st.session_state.get("usuario_logado", "Desconhecido")
                                try:
                                    operacao = cadastrar_movimentacao(
                                        produto_nome=produto_info[1],
                                        custo_inicial=custo_inicial,
                                        preco_venda=produto_info[4],
                                        quantidade=quantidade_nova,
                                        tipo="entrada",
                                        usuario=usuario,
                                        metodo_pagamento=metodo_pagamento,
                                        status="Ativo"
                                    )
                                    st.success("Operação registrada com sucesso!")
                                    st.info(f"Número da operação: {operacao}")
                                except Exception as e:
                                    st.error(f"Erro ao registrar a operação: {e}")
                                st.rerun()
            else:
                st.info("Nenhum produto ativo cadastrado ainda.")

            st.write("---")
            st.subheader("Relatório de Entradas Ativas")

            movimentos = listar_movimentacoes_bd()
            # Filtra movimentações de entrada com status "Ativo"
            # m[7] => tipo, m[10] => status
            entradas_ativas = [
                m for m in movimentos
                if m[7].lower() == "entrada" and m[10].lower() == "ativo"
            ]
            if entradas_ativas:
                # Lembrando que agora temos 12 colunas:
                # 0:id,1:num_operacao,2:data,3:nome,4:custo_inicial,5:preco_venda,
                # 6:quantidade,7:tipo,8:usuario,9:metodo_pagamento,10:status,11:total
                colunas = [
                    "ID","Operação", "Data", "Produto",
                    "Custo Inicial", "Preço de Venda", "Quantidade",
                    "Tipo", "Usuário", "Método Pagamento",
                    "Status", "Total"
                ]
                df_entradas = pd.DataFrame(entradas_ativas, columns=colunas)
                st.dataframe(df_entradas, use_container_width=True)
            else:
                st.info("Nenhuma movimentação de entrada ativa encontrada.")

        # Chama a função
        pagina_entrada_produtos()


def pagina_emitir_venda():
    st.title("🛒 PDV - Emitir Venda (Uma Única Coluna)")

    if "carrinho" not in st.session_state:
        st.session_state.carrinho = {}

    num_colunas = 1
    colunas = st.columns(num_colunas)

    def calcular_saldo(produto_nome, movimentos):
        entradas = sum(
            m[6] for m in movimentos
            if m[3] == produto_nome and m[7].lower() == "entrada" and m[10].lower() == "ativo"
        )
        saidas = sum(
            m[6] for m in movimentos
            if m[3] == produto_nome and m[7].lower() in ("venda", "saída", "saida") and m[10].lower() == "ativo"
        )
        return entradas - saidas

    produtos_db = listar_produtos_bd()
    produtos_ativos = [p for p in produtos_db if p[3] == "Ativo"]
    movimentos = listar_movimentacoes_bd()

    for i, p in enumerate(produtos_ativos):
        with colunas[0]:
            pid, nome, info, status, preco = p
            saldo = calcular_saldo(nome, movimentos)

            st.markdown(f"### {nome} (✅ {saldo} disponíveis)")
            st.markdown(f"**💰 R$ {preco:.2f}**")
            
            if saldo > 0:
                qtd_selecionada = st.number_input(
                    f"Quantidade de {nome}",
                    min_value=1,
                    max_value=saldo,
                    value=1,
                    key=f"qtd_{i}"
                )
            else:
                st.warning("Estoque esgotado!")
                qtd_selecionada = st.number_input(
                    f"Quantidade de {nome}",
                    min_value=0,
                    max_value=0,
                    value=0,
                    key=f"qtd_{i}",
                    disabled=True
                )
            msg_container = st.empty()

            if st.button(f"🛍️ Adicionar {nome}", key=f"add_{i}"):
                if qtd_selecionada > saldo:
                    msg_container.error("Quantidade indisponível no estoque!")
                else:
                    if nome in st.session_state.carrinho:
                        st.session_state.carrinho[nome]["quantidade"] += qtd_selecionada
                    else:
                        st.session_state.carrinho[nome] = {"preco": preco, "quantidade": qtd_selecionada}
                    msg_container.success(f"{qtd_selecionada}x {nome} adicionado ao carrinho!")
            st.markdown("<hr style='border: 1px solid #ddd; margin: 10px 0;'>", unsafe_allow_html=True)

    st.markdown("## 🛒 Carrinho")
    if st.session_state.carrinho:
        total = 0
        itens_remover = []
        for nome, item in st.session_state.carrinho.items():
            subtotal = item["preco"] * item["quantidade"]
            total += subtotal
            with st.container():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"""
                    <div style='background-color: #f8f9fa; padding: 10px; border-radius: 8px;
                    margin-bottom: 8px; border: 1px solid #dee2e6;'>
                        <strong>{item['quantidade']}x {nome}</strong><br>
                        <span style='color: #6c757d;'>Preço unitário: R$ {item['preco']:.2f}</span><br>
                        <strong>Total: R$ {subtotal:.2f}</strong>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    if st.button(f"❌", key=f"remove_{nome}"):
                        itens_remover.append(nome)
        for item in itens_remover:
            del st.session_state.carrinho[item]
            st.warning(f"{item} removido do carrinho.")
        st.markdown(f"""
        <div style='background-color: #fffbeb; padding: 10px; border-radius: 8px;
        margin-top: 12px; border: 1px solid #ffd700; text-align: center;'>
            <h4>💳 Total: R$ {total:.2f}</h4>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🏦 Escolha o método de pagamento:")
        metodo_pagamento = st.radio("Selecione uma opção:", ["Dinheiro", "Pix", "Cartão", "Outro"])
        if metodo_pagamento == "Outro":
            metodo_personalizado = st.text_input("Digite o método de pagamento:")

        # Gerar um número de operação único para toda a venda
        op_num = None
        if st.button("Finalizar Venda"):
            usuario = st.session_state.get("usuario_logado", "Desconhecido")
            # Gera um único número de operação para toda a venda
            for nome, item in st.session_state.carrinho.items():
                quantidade = item["quantidade"]
                preco_unit = item["preco"]
                if op_num is None:
                    # Para o primeiro item, gerar e capturar o número de operação
                    op_num = cadastrar_movimentacao(
                        produto_nome=nome,
                        custo_inicial=0,  # custo_inicial para venda é 0
                        preco_venda=preco_unit,
                        quantidade=quantidade,
                        tipo="venda",
                        usuario=usuario,
                        metodo_pagamento=metodo_pagamento,
                        status="Ativo",
                        num_operacao=None  # Gera novo
                    )
                else:
                    # Para os demais, usar o mesmo número de operação
                    cadastrar_movimentacao(
                        produto_nome=nome,
                        custo_inicial=0,
                        preco_venda=preco_unit,
                        quantidade=quantidade,
                        tipo="venda",
                        usuario=usuario,
                        metodo_pagamento=metodo_pagamento,
                        status="Ativo",
                        num_operacao=op_num
                    )
            st.success("Venda finalizada com sucesso!")
            st.info(f"Número da operação: {op_num}")
            st.session_state.carrinho = {}
            st.rerun()
        
        if st.button("🧹 Limpar Carrinho"):
            st.session_state.carrinho = {}
            st.success("Carrinho limpo!")
            st.rerun()
    else:
        st.markdown(
            "<div style='text-align: center; color: #6c757d; font-size: 18px;'>"
            "🛒 Seu carrinho está vazio.</div>",
            unsafe_allow_html=True,
        )

def pagina_gerenciar_vendas():
    st.title("Gerenciar Vendas")

    st.subheader("Relatório de Vendas Ativas")

    # Carrega todas as movimentações
    movimentos = listar_movimentacoes_bd()
    # Cada linha de movimentos tem 12 colunas (id, num_operacao, data, nome, custo_inicial, preco_venda,
    # quantidade, tipo, usuario, metodo_pagamento, status, total)
    # Precisamos filtrar apenas as que tenham tipo="venda" (ou "saida"/"saída") e status="Ativo"

    saidas_ativas = [
        m for m in movimentos
        if m[7].lower() in ("venda", "saida", "saída") and m[10].lower() == "ativo"
    ]

    if saidas_ativas:
        colunas = [
            "ID", "Operação", "Data", "Produto",
            "Custo Inicial", "Preço de Venda", "Quantidade",
            "Tipo", "Usuário", "Método Pagamento", "Status", "Total"
        ]
        df_saidas = pd.DataFrame(saidas_ativas, columns=colunas)
        st.dataframe(df_saidas, use_container_width=True)
    else:
        st.info("Nenhuma venda ativa encontrada.")


























def pagina_financeiro():
    st.title("Financeiro")
    st.write("Resumo financeiro, relatórios... (exemplo)")

def pagina_gerenciar_usuarios():
    st.title("Gerenciar Usuários")

    st.subheader("Cadastrar Novo Usuário")
    with st.form("cadastro_novo_usuario"):
        novo_login  = st.text_input("Novo Login")
        nova_senha = st.text_input("Senha", type="password")
        st.write("Permissões do Novo Usuário:")
        perm_cad_produtos  = st.checkbox("Cadastrar Produtos")
        perm_ger_vendas    = st.checkbox("Gerenciar Vendas")
        perm_emit_venda    = st.checkbox("Emitir Venda")
        perm_financeiro    = st.checkbox("Financeiro")
        perm_geren_user    = st.checkbox("Gerenciar Usuários")

        if st.form_submit_button("Cadastrar"):
            sucesso = cadastrar_usuario_bd(
                login=novo_login,
                senha=nova_senha,
                perm_cadastrar_produtos=perm_cad_produtos,
                perm_estornar_produtos=perm_ger_vendas,
                perm_emitir_venda=perm_emit_venda,
                perm_financeiro=perm_financeiro,
                perm_gerenciar_usuarios=perm_geren_user
            )
            if sucesso:
                st.success(f"Usuário '{novo_login}' cadastrado com sucesso!")
            else:
                st.error(f"Não foi possível cadastrar. Usuário '{novo_login}' já existe ou erro no banco.")

    st.write("---")
    st.subheader("Lista de Usuários Cadastrados")
    usuarios = listar_usuarios_bd()
    if not usuarios:
        st.info("Nenhum usuário cadastrado.")
        return

    colunas = [
        "id", "login", "senha",
        "perm_cadastrar_produtos", "perm_gerenciar_vendas",
        "perm_emit_venda", "perm_financeiro", "perm_gerenciar_usuarios"
    ]
    df = pd.DataFrame(usuarios, columns=colunas)
    st.dataframe(df, use_container_width=True)

    opcoes = [f"{u[0]} - {u[1]}" for u in usuarios]
    escolha = st.selectbox("Selecione um usuário:", opcoes)
    if escolha:
        user_id = int(escolha.split(" - ")[0])
        user_info = next((u for u in usuarios if u[0] == user_id), None)
        if user_info:
            (id_, login_, senha_,
             p_cad_prod, p_est_prod,
             p_emit_venda, p_fin,
             p_gerenciar) = user_info

            st.write(f"**Editando usuário:** {login_} (ID={id_})")
            with st.form("editar_usuario"):
                nova_senha = st.text_input("Nova Senha (vazio = não alterar)", type="password")
                cad_prod_edit   = st.checkbox("Cadastrar Produtos", value=bool(p_cad_prod))
                est_prod_edit   = st.checkbox("Gerenciar Vendas", value=bool(p_est_prod))
                emit_venda_edit = st.checkbox("Emitir Venda", value=bool(p_emit_venda))
                fin_edit        = st.checkbox("Financeiro", value=bool(p_fin))
                gerenciar_edit  = st.checkbox("Gerenciar Usuários", value=bool(p_gerenciar))

                if st.form_submit_button("Salvar"):
                    if not nova_senha:
                        nova_senha = senha_
                    atualizar_usuario_bd(
                        user_id=id_,
                        nova_senha=nova_senha,
                        cad_produtos=cad_prod_edit,
                        est_prod=est_prod_edit,
                        emit_venda=emit_venda_edit,
                        financeiro=fin_edit,
                        gerenciar_usuarios=gerenciar_edit
                    )
                    st.success(f"Usuário {login_} atualizado!")
                    st.rerun()

            if st.button("Excluir Usuário"):
                excluir_usuario_bd(id_)
                st.warning(f"Usuário '{login_}' excluído!")
                st.rerun()

################################################
# MAIN
################################################

def main():
    st.title("Sistema de Login - Menu Lateral (option_menu)")

    criar_banco_de_dados()

    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
    if "usuario_logado" not in st.session_state:
        st.session_state.usuario_logado = ""
    if "permissoes" not in st.session_state:
        st.session_state.permissoes = {}

    if not st.session_state.autenticado:
        login_input = st.text_input("Login")
        senha_input = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            # Verifica Master
            if login_input == "Master" and senha_input == "1235":
                st.session_state.autenticado = True
                st.session_state.usuario_logado = "Master"
                st.session_state.permissoes = {
                    "cadastrar_produtos":  True,
                    "gerenciar_vendas":    True,
                    "emitir_venda":        True,
                    "financeiro":          True,
                    "gerenciar_usuarios":  True
                }
                st.rerun()
            else:
                user_db = buscar_usuario_bd(login_input, senha_input)
                if user_db:
                    st.session_state.autenticado = True
                    st.session_state.usuario_logado = user_db[1]
                    # user_db => (id, login, senha, perm_cad_prod, perm_est_prod, perm_emit_venda, perm_fin, perm_geren_user)
                    st.session_state.permissoes = {
                        "cadastrar_produtos": bool(user_db[3]),
                        "gerenciar_vendas":   bool(user_db[4]),
                        "emitir_venda":       bool(user_db[5]),
                        "financeiro":         bool(user_db[6]),
                        "gerenciar_usuarios": bool(user_db[7])
                    }
                    st.rerun()
                else:
                    st.error("Login inválido.")
    else:
        st.success(f"Bem-vindo, {st.session_state.usuario_logado}!")
        perms = st.session_state.permissoes
        menu_opcoes = []
        menu_icones = []

        if perms.get("gerenciar_usuarios"):
            menu_opcoes.append("Gerenciar Usuários")
            menu_icones.append("people")
        if perms.get("cadastrar_produtos"):
            menu_opcoes.append("Cadastrar Produtos")
            menu_icones.append("box-arrow-in-down")
        if perms.get("gerenciar_vendas"):
            menu_opcoes.append("Gerenciar Vendas")
            menu_icones.append("arrow-counterclockwise")
        if perms.get("emitir_venda"):
            menu_opcoes.append("Emitir Venda")
            menu_icones.append("cart-check")
        if perms.get("financeiro"):
            menu_opcoes.append("Financeiro")
            menu_icones.append("wallet2")

        menu_opcoes.append("Sair")
        menu_icones.append("door-closed")

        with st.sidebar:
            selected = option_menu(
                "Menu Lateral",
                menu_opcoes,
                icons=menu_icones,
                menu_icon="cast",
                default_index=0,
                orientation="vertical",
                key="menu_principal"
            )

        if selected == "Gerenciar Usuários":
            pagina_gerenciar_usuarios()
        elif selected == "Cadastrar Produtos":
            pagina_cadastrar_produtos()
        elif selected == "Gerenciar Vendas":
            pagina_gerenciar_vendas()
        elif selected == "Emitir Venda":
            pagina_emitir_venda()
        elif selected == "Financeiro":
            pagina_financeiro()
        elif selected == "Sair":
            st.session_state.autenticado = False
            st.session_state.usuario_logado = ""
            st.session_state.permissoes = {}
            st.rerun()
        else:
            st.write("Selecione uma das opções no menu lateral.")

if __name__ == "__main__":
    main()
