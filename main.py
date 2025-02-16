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
    excluir_produto_bd
)

################################################
# PÁGINAS (funções para cada permissão)
################################################

def pagina_cadastrar_produtos():
    st.title("Gerenciar Produtos")

    # Cria duas abas
    tab1, tab2 = st.tabs(["Cadastrar/Editar Produtos", "Funcionalidade Futura"])

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

    # Aba 2 (futura)
    with tab2:
        st.write("Em desenvolvimento...")



def pagina_estornar_produtos():
    st.title("Estornar Produtos")
    st.write("Log de estornos, etc... (exemplo)")

def pagina_emitir_venda():
    st.title("Emitir Venda")
    st.write("Formulário/lógica para emitir vendas... (exemplo)")

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
        perm_est_prod      = st.checkbox("Estornar Produtos")
        perm_emit_venda    = st.checkbox("Emitir Venda")
        perm_financeiro    = st.checkbox("Financeiro")
        perm_geren_user    = st.checkbox("Gerenciar Usuários")

        if st.form_submit_button("Cadastrar"):
            sucesso = cadastrar_usuario_bd(
            login=novo_login,
            senha=nova_senha,
            perm_cadastrar_produtos=perm_cad_produtos,
            perm_estornar_produtos=perm_est_prod,
            perm_emitir_venda=perm_emit_venda,  # <--- agora usando o nome correto
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
        "perm_estornar_produtos",
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
                est_prod_edit   = st.checkbox("Estornar Produtos", value=bool(p_est_prod))
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
                    "estornar_produtos":   True,
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
                        "estornar_produtos":  bool(user_db[4]),
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
        if perms.get("estornar_produtos"):
            menu_opcoes.append("Estornar Produtos")
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
        elif selected == "Estornar Produtos":
            pagina_estornar_produtos()
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
