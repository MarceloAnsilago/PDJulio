# import streamlit as st
# import pandas as pd
# from database import (
#     criar_banco_de_dados,
#     buscar_usuario_bd,
#     cadastrar_usuario_bd,
#     listar_usuarios_bd,
#     excluir_usuario_bd,
#     atualizar_usuario_bd
# )

# ################################################
# #  PÁGINAS (funções para cada permissão)
# ################################################

# def pagina_cadastrar_produtos():
#     st.title("Cadastrar Produtos")
#     st.write("Conteúdo para cadastrar produtos... (exemplo)")

# def pagina_estornar_produtos():
#     st.title("Estornar Produtos")
#     st.write("Log de estornos, etc... (exemplo)")

# def pagina_emitir_venda():
#     st.title("Emitir Venda")
#     st.write("Formulário/lógica para emitir vendas... (exemplo)")

# def pagina_financeiro():
#     st.title("Financeiro")
#     st.write("Resumo financeiro, relatórios... (exemplo)")

# def pagina_gerenciar_usuarios():
#     """
#     Nesta página fazemos:
#       1. Cadastrar Novo Usuário (formulário)
#       2. Listar / Editar / Excluir Usuários cadastrados
#     """
#     st.title("Gerenciar Usuários")

#     ###########################
#     # FORMULÁRIO DE CADASTRO
#     ###########################
#     st.subheader("Cadastrar Novo Usuário")
#     with st.form("cadastro_novo_usuario"):
#         novo_login  = st.text_input("Novo Login")
#         nova_senha = st.text_input("Senha", type="password")

#         st.write("Permissões do Novo Usuário:")
#         perm_cad_produtos  = st.checkbox("Cadastrar Produtos")
#         perm_est_prod      = st.checkbox("Estornar Produtos")
#         perm_emit_venda    = st.checkbox("Emitir Venda")
#         perm_financeiro    = st.checkbox("Financeiro")
#         perm_geren_user    = st.checkbox("Gerenciar Usuários")

#         if st.form_submit_button("Cadastrar"):
#             # Chama a função do BD para inserir
#             sucesso = cadastrar_usuario_bd(
#                 login=novo_login,
#                 senha=nova_senha,
#                 perm_cadastrar_produtos=perm_cad_produtos,
#                 perm_estornar_produtos=perm_est_prod,
#                 perm_emit_venda=perm_emit_venda,
#                 perm_financeiro=perm_financeiro,
#                 perm_gerenciar_usuarios=perm_geren_user
#             )
#             if sucesso:
#                 st.success(f"Usuário '{novo_login}' cadastrado com sucesso!")
#             else:
#                 st.error(f"Não foi possível cadastrar. Usuário '{novo_login}' já existe ou erro no banco.")

#     st.write("---")  # Divisor visual

#     ###########################
#     # LISTAR / EDITAR / EXCLUIR
#     ###########################
#     st.subheader("Lista de Usuários Cadastrados")
#     usuarios = listar_usuarios_bd()
    
#     if not usuarios:
#         st.info("Nenhum usuário cadastrado.")
#         return
    
#     # Cada linha do BD tem 8 colunas:
#     # (id, login, senha,
#     #  perm_cadastrar_produtos, perm_estornar_produtos,
#     #  perm_emitir_venda, perm_financeiro, perm_gerenciar_usuarios)
#     colunas = [
#         "id", 
#         "login", 
#         "senha",
#         "perm_cadastrar_produtos",
#         "perm_estornar_produtos",
#         "perm_emitir_venda",
#         "perm_financeiro",
#         "perm_gerenciar_usuarios"
#     ]
#     df = pd.DataFrame(usuarios, columns=colunas)
#     st.dataframe(df, use_container_width=True)

#     # Escolher um usuário para editar/excluir
#     opcoes = [f"{u[0]} - {u[1]}" for u in usuarios]  # "id - login"
#     escolha = st.selectbox("Selecione um usuário:", opcoes)
    
#     if escolha:
#         user_id = int(escolha.split(' - ')[0])
        
#         # Localiza o usuário selecionado
#         user_info = next((u for u in usuarios if u[0] == user_id), None)
#         if user_info:
#             (id_, login_, senha_,
#              p_cad_prod, p_est_prod,
#              p_emit_venda, p_fin,
#              p_gerenciar) = user_info

#             st.write(f"**Editando usuário:** {login_} (ID={id_})")

#             with st.form("editar_usuario"):
#                 nova_senha = st.text_input("Nova Senha (vazio = não alterar)", type="password")
#                 cad_prod_edit   = st.checkbox("Cadastrar Produtos", value=bool(p_cad_prod))
#                 est_prod_edit   = st.checkbox("Estornar Produtos", value=bool(p_est_prod))
#                 emit_venda_edit = st.checkbox("Emitir Venda", value=bool(p_emit_venda))
#                 fin_edit        = st.checkbox("Financeiro", value=bool(p_fin))
#                 gerenciar_edit  = st.checkbox("Gerenciar Usuários", value=bool(p_gerenciar))

#                 if st.form_submit_button("Salvar"):
#                     # Se a nova_senha estiver em branco, mantemos a senha anterior
#                     if not nova_senha:
#                         nova_senha = senha_
#                     # Função de update no banco
#                     atualizar_usuario_bd(
#                         user_id=id_,
#                         nova_senha=nova_senha,
#                         cad_produtos=cad_prod_edit,
#                         est_prod=est_prod_edit,
#                         emit_venda=emit_venda_edit,
#                         financeiro=fin_edit,
#                         gerenciar_usuarios=gerenciar_edit
#                     )
#                     st.success(f"Usuário {login_} atualizado!")
#                     st.rerun()

#             if st.button("Excluir Usuário"):
#                 excluir_usuario_bd(id_)
#                 st.warning(f"Usuário '{login_}' excluído!")
#                 st.rerun()

# def pagina_minhas_permissoes():
#     """Exibe as permissões do usuário logado."""
#     st.title("Minhas Permissões")
#     perms = st.session_state.get("permissoes", {})
#     if not perms:
#         st.write("Nenhuma permissão encontrada.")
#         return
#     for k, v in perms.items():
#         st.write(f"• {k}: **{v}**")

# ################################################
# #  MENU LATERAL (um botão para cada permissão)
# ################################################

# def exibir_menu_lateral(perms: dict):
#     st.sidebar.title("Menu Lateral")

#     pagina_clicada = None

#     # Se perm_gerenciar_usuarios for True, mostra "Gerenciar Usuários"
#     if perms.get("gerenciar_usuarios"):
#         if st.sidebar.button("Gerenciar Usuários"):
#             pagina_clicada = "gerenciar_usuarios"

#     if perms.get("cadastrar_produtos"):
#         if st.sidebar.button("Cadastrar Produtos"):
#             pagina_clicada = "cad_produtos"

#     if perms.get("estornar_produtos"):
#         if st.sidebar.button("Estornar Produtos"):
#             pagina_clicada = "estornar_produtos"

#     if perms.get("emitir_venda"):
#         if st.sidebar.button("Emitir Venda"):
#             pagina_clicada = "emitir_venda"

#     if perms.get("financeiro"):
#         if st.sidebar.button("Financeiro"):
#             pagina_clicada = "financeiro"

#     # Uma página geral que todo mundo pode ver
#     if st.sidebar.button("Minhas Permissões"):
#         pagina_clicada = "minhas_permissoes"

#     # Botão de sair
#     if st.sidebar.button("Sair"):
#         pagina_clicada = "sair"

#     return pagina_clicada

# ################################################
# # MAIN
# ################################################

# def main():
#     st.title("Sistema de Login - Exemplo (Sem perm_cadastrar_usuarios)")

#     criar_banco_de_dados()

#     if "autenticado" not in st.session_state:
#         st.session_state.autenticado = False
#     if "usuario_logado" not in st.session_state:
#         st.session_state.usuario_logado = ""
#     if "permissoes" not in st.session_state:
#         st.session_state.permissoes = {}

#     if not st.session_state.autenticado:
#         # LOGIN
#         login_input = st.text_input("Login")
#         senha_input = st.text_input("Senha", type="password")

#         if st.button("Entrar"):
#             # Verifica Master (hard-coded)
#             if login_input == "Master" and senha_input == "1235":
#                 st.session_state.autenticado = True
#                 st.session_state.usuario_logado = "Master"
#                 # Master tem tudo liberado
#                 st.session_state.permissoes = {
#                     "cadastrar_produtos":  True,
#                     "estornar_produtos":   True,
#                     "emitir_venda":        True,
#                     "financeiro":          True,
#                     "gerenciar_usuarios":  True
#                 }
#                 st.rerun()
#             else:
#                 # Caso não seja Master, verifica no BD
#                 user_db = buscar_usuario_bd(login_input, senha_input)
#                 if user_db:
#                     # user_db = (id, login, senha,
#                     #            perm_cadastrar_produtos,
#                     #            perm_estornar_produtos,
#                     #            perm_emitir_venda,
#                     #            perm_financeiro,
#                     #            perm_gerenciar_usuarios)
#                     st.session_state.autenticado = True
#                     st.session_state.usuario_logado = user_db[1]  # login
#                     st.session_state.permissoes = {
#                         "cadastrar_produtos": bool(user_db[3]),
#                         "estornar_produtos":  bool(user_db[4]),
#                         "emitir_venda":      bool(user_db[5]),
#                         "financeiro":        bool(user_db[6]),
#                         "gerenciar_usuarios":bool(user_db[7])
#                     }
#                     st.rerun()
#                 else:
#                     st.error("Login inválido.")
#     else:
#         # Já autenticado
#         st.success(f"Bem-vindo, {st.session_state.usuario_logado}!")

#         # Exibe menu lateral
#         pagina_clicada = exibir_menu_lateral(st.session_state.permissoes)
#         if pagina_clicada:
#             st.session_state["pagina_selecionada"] = pagina_clicada

#         pagina = st.session_state.get("pagina_selecionada", None)

#         if pagina == "gerenciar_usuarios":
#             pagina_gerenciar_usuarios()
#         elif pagina == "cad_produtos":
#             pagina_cadastrar_produtos()
#         elif pagina == "estornar_produtos":
#             pagina_estornar_produtos()
#         elif pagina == "emitir_venda":
#             pagina_emitir_venda()
#         elif pagina == "financeiro":
#             pagina_financeiro()
#         elif pagina == "minhas_permissoes":
#             pagina_minhas_permissoes()
#         elif pagina == "sair":
#             st.session_state.autenticado = False
#             st.session_state.usuario_logado = ""
#             st.session_state.permissoes = {}
#             st.session_state.pagina_selecionada = None
#             st.rerun()
#         else:
#             st.write("Selecione uma das opções no menu lateral.")

# if __name__ == "__main__":
#     main()
import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu  # Biblioteca para menu estilizado

from database import (
    criar_banco_de_dados,
    buscar_usuario_bd,
    cadastrar_usuario_bd,
    listar_usuarios_bd,
    excluir_usuario_bd,
    atualizar_usuario_bd
)

################################################
#  PÁGINAS (funções para cada permissão)
################################################

def pagina_cadastrar_produtos():
    st.title("Cadastrar Produtos")
    st.write("Conteúdo para cadastrar produtos... (exemplo)")

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
    Nesta página fazemos:
      1. Cadastrar Novo Usuário (formulário)
      2. Listar / Editar / Excluir Usuários cadastrados
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
            # Chama a função do BD para inserir
            sucesso = cadastrar_usuario_bd(
                login=novo_login,
                senha=nova_senha,
                perm_cadastrar_produtos=perm_cad_produtos,
                perm_estornar_produtos=perm_est_prod,
                perm_emit_venda=perm_emit_venda,
                perm_financeiro=perm_financeiro,
                perm_gerenciar_usuarios=perm_geren_user
            )
            if sucesso:
                st.success(f"Usuário '{novo_login}' cadastrado com sucesso!")
            else:
                st.error(f"Não foi possível cadastrar. Usuário '{novo_login}' já existe ou erro no banco.")

    st.write("---")  # Divisor visual

    ###########################
    # LISTAR / EDITAR / EXCLUIR
    ###########################
    st.subheader("Lista de Usuários Cadastrados")
    usuarios = listar_usuarios_bd()
    
    if not usuarios:
        st.info("Nenhum usuário cadastrado.")
        return
    
    # Cada linha do BD tem 8 colunas:
    # (id, login, senha,
    #  perm_cadastrar_produtos, perm_estornar_produtos,
    #  perm_emitir_venda, perm_financeiro, perm_gerenciar_usuarios)
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

    # Escolher um usuário para editar/excluir
    opcoes = [f"{u[0]} - {u[1]}" for u in usuarios]  # "id - login"
    escolha = st.selectbox("Selecione um usuário:", opcoes)
    
    if escolha:
        user_id = int(escolha.split(' - ')[0])
        
        # Localiza o usuário selecionado
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
                    # Se a nova_senha estiver em branco, mantemos a senha anterior
                    if not nova_senha:
                        nova_senha = senha_
                    # Função de update no banco
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

    # Controle de sessão
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
    if "usuario_logado" not in st.session_state:
        st.session_state.usuario_logado = ""
    if "permissoes" not in st.session_state:
        st.session_state.permissoes = {}

    # Form de Login se não estiver autenticado
    if not st.session_state.autenticado:
        login_input = st.text_input("Login")
        senha_input = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            # Verifica Master (hard-coded)
            if login_input == "Master" and senha_input == "1235":
                st.session_state.autenticado = True
                st.session_state.usuario_logado = "Master"
                # Master com todas as permissões
                st.session_state.permissoes = {
                    "cadastrar_produtos":  True,
                    "estornar_produtos":   True,
                    "emitir_venda":        True,
                    "financeiro":          True,
                    "gerenciar_usuarios":  True
                }
                st.rerun()
            else:
                # Caso não seja Master, verifica no BD
                user_db = buscar_usuario_bd(login_input, senha_input)
                if user_db:
                    st.session_state.autenticado = True
                    st.session_state.usuario_logado = user_db[1]  # login
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
        # Já autenticado
        st.success(f"Bem-vindo, {st.session_state.usuario_logado}!")

        # Monta a lista de páginas (opções) e ícones com base nas permissões
        menu_opcoes = []
        menu_icones = []

        perms = st.session_state.permissoes

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

        # Sempre adicionamos "Sair"
        menu_opcoes.append("Sair")
        menu_icones.append("door-closed")

        # Aqui criamos o menu LATERAL com orientation vertical
        from streamlit_option_menu import option_menu
        with st.sidebar:
            selected = option_menu(
                "Menu Lateral",
                menu_opcoes,
                icons=menu_icones,
                menu_icon="cast",  # ícone do menu principal
                default_index=0,   # primeira opção selecionada por padrão
                orientation="vertical"  # menu lateral (vertical)
            )

        # Lógica de navegação
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
            # Desloga
            st.session_state.autenticado = False
            st.session_state.usuario_logado = ""
            st.session_state.permissoes = {}
            st.rerun()
        else:
            # Se por algum motivo não cair em nenhum
            st.write("Selecione uma das opções no menu lateral.")


if __name__ == "__main__":
    main()
