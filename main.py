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
# PÁGINAS (funções para cada permissão)
################################################

def pagina_cadastrar_produtos():
    st.title("Gerenciar Produtos")

    # Cria duas abas
    tab1, tab2 = st.tabs(["Cadastrar/Editar Produtos", "Entrada de Produtos"])

    with tab1:
        ###########################
        # 1) FORMULÁRIO DE CADASTRO
        ###########################
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

        ###########################
        # 2) LISTAR PRODUTOS
        ###########################
        st.subheader("Lista de Produtos Cadastrados")
        produtos = listar_produtos_bd()
        if not produtos:
            st.info("Nenhum produto cadastrado ainda.")
            return  # Se não há produtos, encerra a função aqui

        # Supondo que 'listar_produtos_bd()' retorne: (id, nome, info, status, preco)
        df = pd.DataFrame(produtos, columns=["ID", "Nome", "Info", "Status", "Preço"])
        st.dataframe(df, use_container_width=True)

        ###########################
        # 3) EDITAR PRODUTO
        ###########################
        opcoes = [f"{p[0]} - {p[1]}" for p in produtos]  # ex: "1 - Camiseta"
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



    with tab2:
        def pagina_entrada_produtos():
            st.title("Entrada de Produtos")
            
            # Filtra os produtos ativos (Status = "Ativo")
            produtos_todos = listar_produtos_bd()
            produtos = [p for p in produtos_todos if p[3] == "Ativo"]  # p[3] é "Status"
            
            if produtos:
                df = pd.DataFrame(produtos, columns=["ID", "Nome", "Info", "Status", "Preço"])
                st.dataframe(df, use_container_width=True)
                
                # Combobox para selecionar o produto
                opcoes = [f"{p[0]} - {p[1]}" for p in produtos]
                escolha = st.selectbox("Selecione um produto para entrada:", opcoes)
                
                if escolha:
                    produto_id = int(escolha.split(" - ")[0])
                    produto_info = next((p for p in produtos if p[0] == produto_id), None)
                    if produto_info:
                        st.write(f"Produto selecionado: {escolha}")
                        
                        # Calcular o saldo atual do produto
                        movimentos = listar_movimentacoes_bd()
                        entradas = sum(m[5] for m in movimentos 
                                    if m[2] == produto_info[1] 
                                    and m[6].lower() == "entrada" 
                                    and m[9].lower() == "ativo")
                        saidas = sum(m[5] for m in movimentos 
                                    if m[2] == produto_info[1] 
                                    and m[6].lower() in ("saída", "saida") 
                                    and m[9].lower() == "ativo")
                        saldo_atual = entradas - saidas
                        
                        with st.form("form_entrada_produto"):
                            # Ordem dos campos conforme solicitado:
                            # 1. Quantidade a Registrar
                            quantidade_nova = st.number_input("Quantidade a Registrar", min_value=1, step=1)
                            # 2. Custo Inicial (ativo - usuário pode inserir)
                            custo_inicial = st.number_input("Custo Inicial (por unidade)", min_value=0.0, format="%.2f")
                            # 3. Preço de Venda (desabilitado - valor do produto)
                            preco_venda = st.number_input("Preço de Venda (por unidade)", min_value=0.0,
                                                        value=produto_info[4], disabled=True, format="%.2f")
                            # 4. Saldo Atual (desabilitado)
                            st.number_input("Saldo Atual", value=float(saldo_atual), disabled=True, format="%.0f")
                            # 5. Método de Pagamento
                            metodo_pagamento = st.selectbox("Método de Pagamento", ["Dinheiro", "Cartão", "Cheque", "Outro"])
                            
                            submit = st.form_submit_button("Registrar Entrada")
                            
                            if submit:
                                usuario = st.session_state.get("usuario_logado", "Desconhecido")
                                try:
                                    cadastrar_movimentacao(
                                        produto_nome=produto_info[1],
                                        custo_inicial=custo_inicial,
                                        preco_venda=produto_info[4],
                                        quantidade=quantidade_nova,
                                        tipo="entrada",
                                        usuario=usuario,
                                        metodo_pagamento=metodo_pagamento,
                                        status="Ativo"
                                    )
                                    st.success("Entrada registrada com sucesso!")
                                except Exception as e:
                                    st.error(f"Erro ao registrar a entrada: {e}")
                                st.rerun()
            else:
                st.info("Nenhum produto ativo cadastrado ainda.")
            
            st.write("---")
            st.subheader("Relatório de Entradas Ativas")
            movimentos = listar_movimentacoes_bd()
            # Filtra as movimentações de entrada com status "Ativo"
            entradas_ativas = [m for m in movimentos if m[6].lower() == "entrada" and m[9].lower() == "ativo"]
            if entradas_ativas:
                colunas = ["ID", "Data", "Produto", "Custo Inicial", "Preço de Venda", "Quantidade", 
                        "Tipo", "Usuário", "Método Pagamento", "Status", "Total"]
                df_entradas = pd.DataFrame(entradas_ativas, columns=colunas)
                st.dataframe(df_entradas, use_container_width=True)
            else:
                st.info("Nenhuma movimentação de entrada ativa encontrada.")
        
        # Chama a função para exibir o conteúdo da Tab 2
        pagina_entrada_produtos()




def pagina_emitir_venda():
    from database import (
        listar_produtos_bd,
        listar_movimentacoes_bd,
        cadastrar_movimentacao
    )

    st.title("🛒 PDV - Emitir Venda (Uma Única Coluna)")

    # Inicializa o carrinho na sessão, se ainda não existir
    if "carrinho" not in st.session_state:
        st.session_state.carrinho = {}

    # Define que só haverá 1 coluna (modo mobile fixo)
    num_colunas = 1
    colunas = st.columns(num_colunas)

    # Função para calcular o saldo atual de um produto
    def calcular_saldo(produto_nome, movimentos):
        entradas = sum(m[5] for m in movimentos
                       if m[2] == produto_nome and m[6].lower() == "entrada" and m[9].lower() == "ativo")
        saidas = sum(m[5] for m in movimentos
                     if m[2] == produto_nome and m[6].lower() in ("venda", "saída", "saida") and m[9].lower() == "ativo")
        return entradas - saidas

    # Buscar produtos ativos e movimentações
    produtos_db = listar_produtos_bd()
    produtos_ativos = [p for p in produtos_db if p[3] == "Ativo"]  # p[3] é status
    movimentos = listar_movimentacoes_bd()

    # Exibir produtos (todos em uma única coluna)
    for i, p in enumerate(produtos_ativos):
        with colunas[0]:  # sempre a mesma coluna (índice 0)
            # p: (id, nome, info, status, preco)
            pid, nome, info, status, preco = p
            saldo = calcular_saldo(nome, movimentos)

            st.markdown(f"### {nome} (✅ {saldo} disponíveis)")
            st.markdown(f"**💰 R$ {preco:.2f}**")

            qtd_selecionada = st.number_input(
                f"Quantidade de {nome}",
                min_value=1,
                max_value=saldo if saldo > 0 else 0,
                value=1,
                key=f"qtd_{i}"
            )

            msg_container = st.empty()

            # Botão para adicionar ao carrinho
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

    # Exibir o carrinho
    st.markdown("## 🛒 Carrinho")
    if st.session_state.carrinho:
        total = 0
        itens_remover = []

        # Exibir itens do carrinho em cards
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

        # Remover itens marcados
        for item in itens_remover:
            del st.session_state.carrinho[item]
            st.warning(f"{item} removido do carrinho.")

        st.markdown(f"""
        <div style='background-color: #fffbeb; padding: 10px; border-radius: 8px;
        margin-top: 12px; border: 1px solid #ffd700; text-align: center;'>
            <h4>💳 Total: R$ {total:.2f}</h4>
        </div>
        """, unsafe_allow_html=True)

        # Escolha do método de pagamento
        st.markdown("### 🏦 Escolha o método de pagamento:")
        metodo_pagamento = st.radio("Selecione uma opção:", ["Dinheiro", "Pix", "Cartão", "Outro"])
        if metodo_pagamento == "Outro":
            metodo_personalizado = st.text_input("Digite o método de pagamento:")

        # Botão para finalizar a venda
        if st.button("Finalizar Venda"):
            usuario = st.session_state.get("usuario_logado", "Desconhecido")
            for nome, item in st.session_state.carrinho.items():
                quantidade = item["quantidade"]
                preco_unit = item["preco"]
                try:
                    # custo_inicial = 0 (como solicitado)
                    # preco_venda = preco_unit
                    # A função no banco deve calcular total usando preco_venda
                    cadastrar_movimentacao(
                        produto_nome=nome,
                        custo_inicial=0,       # custo inicial fixo em 0
                        preco_venda=preco_unit,
                        quantidade=quantidade,
                        tipo="venda",
                        usuario=usuario,
                        metodo_pagamento=metodo_pagamento,
                        status="Ativo"
                    )
                except Exception as e:
                    st.error(f"Erro ao registrar venda de {nome}: {e}")
            st.success("Venda finalizada com sucesso!")
            st.session_state.carrinho = {}
            st.rerun()

        # Botão para limpar o carrinho
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
    st.write("Log de estornos, etc... (exemplo)")

def pagina_financeiro():
    st.title("Financeiro")
    st.write("Resumo financeiro, relatórios... (exemplo)")

def pagina_gerenciar_usuarios():
    """
    Nesta página:
      1. Cadastra novo usuário (formulário)
      2. Lista/edita/exclui usuários cadastrados
    """
    st.title("Gerenciar Usuários")

    ###########################
    # FORMULÁRIO DE CADASTRO
    ###########################
    st.subheader("Cadastrar Novo Usuário")
    with st.form("cadastro_novo_usuario"):
        novo_login  = st.text_input("Novo Login")
        nova_senha = st.text_input("Senha", type="password")

        st.write("Permissões do Novo Usuário:")
        perm_cad_produtos  = st.checkbox("Cadastrar Produtos")
        perm_ger_vendas     = st.checkbox("Gerenciar Vendas")
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
        "id", 
        "login", 
        "senha",
        "perm_cadastrar_produtos",
        "perm_gerenciar_vendas",
        "perm_emitir_venda",
        "perm_financeiro",
        "perm_gerenciar_usuarios"
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

    # Cria as tabelas 'usuarios' e 'produtos'
    criar_banco_de_dados()

    # Inicializa variáveis de sessão
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
    if "usuario_logado" not in st.session_state:
        st.session_state.usuario_logado = ""
    if "permissoes" not in st.session_state:
        st.session_state.permissoes = {}

    # Tela de LOGIN se não autenticado
    if not st.session_state.autenticado:
        login_input = st.text_input("Login")
        senha_input = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            if login_input == "Master" and senha_input == "1235":
                st.session_state.autenticado = True
                st.session_state.usuario_logado = "Master"
                st.session_state.permissoes = {
                    "cadastrar_produtos":  True,
                    "gerenciar_vendas":   True,
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
                    st.session_state.permissoes = {
                        "cadastrar_produtos": bool(user_db[3]),
                        "gerenciar_vendas":  bool(user_db[4]),
                        "emitir_venda":      bool(user_db[5]),
                        "financeiro":        bool(user_db[6]),
                        "gerenciar_usuarios":bool(user_db[7])
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