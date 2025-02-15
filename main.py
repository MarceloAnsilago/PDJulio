import streamlit as st
import pandas as pd
from database import (
    criar_banco_de_dados,
    buscar_usuario_bd,
    cadastrar_usuario_bd,
    listar_usuarios_bd,
    excluir_usuario_bd,
    atualizar_usuario_bd
)

##############################
# PÁGINAS (funções)          #
##############################

def pagina_cadastrar_usuarios():
    st.title("Cadastrar Usuários")
    st.write("Formulário ou lógica para cadastrar usuários... (exemplo)")

def pagina_cadastrar_produtos():
    st.title("Cadastrar Produtos")
    st.write("Formulário ou lógica para cadastrar produtos... (exemplo)")

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
    Exemplo da página onde o Master (ou quem tiver permissão) gerencia 
    todos os usuários, podendo editar/excluir. 
    """
    st.title("Gerenciar Usuários")
    usuarios = listar_usuarios_bd()
    
    if not usuarios:
        st.info("Nenhum usuário cadastrado.")
        return
    
    colunas = [
        "id", "login", "senha",
        "perm_cadastrar_usuarios",
        "perm_cadastrar_produtos",
        "perm_estornar_produtos",
        "perm_emitir_venda",
        "perm_financeiro"
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
             p_cad_usr, p_cad_prod, 
             p_est_prod, p_emit_venda, p_fin) = user_info
            
            st.write(f"**Editando usuário:** {login_} (ID={id_})")
            
            with st.form("editar_usuario"):
                nova_senha = st.text_input("Nova Senha (vazio = não alterar)", type="password")
                cad_usr_edit = st.checkbox("Cadastrar Usuários", value=bool(p_cad_usr))
                cad_prod_edit = st.checkbox("Cadastrar Produtos", value=bool(p_cad_prod))
                est_prod_edit = st.checkbox("Estornar Produtos", value=bool(p_est_prod))
                emit_venda_edit = st.checkbox("Emitir Venda", value=bool(p_emit_venda))
                fin_edit = st.checkbox("Financeiro", value=bool(p_fin))

                if st.form_submit_button("Salvar"):
                    if not nova_senha:
                        nova_senha = senha_
                    atualizar_usuario_bd(
                        id_,
                        nova_senha,
                        cad_usr_edit,
                        cad_prod_edit,
                        est_prod_edit,
                        emit_venda_edit,
                        fin_edit
                    )
                    st.success(f"Usuário {login_} atualizado!")
                    st.rerun()

            if st.button("Excluir Usuário"):
                excluir_usuario_bd(id_)
                st.warning(f"Usuário '{login_}' excluído!")
                st.rerun()

def pagina_minhas_permissoes():
    """
    Página que exibe as permissões do usuário logado.
    Se quiser, poderia exibir do BD ou de st.session_state.
    """
    st.title("Minhas Permissões")
    perms = st.session_state.get("permissoes", {})
    if not perms:
        st.write("Nenhuma permissão encontrada.")
        return
    for k, v in perms.items():
        st.write(f"• {k}: **{v}**")

##############################
# FUNÇÃO PARA O MENU LATERAL #
##############################

def exibir_menu_lateral(perms: dict):
    """
    Recebe as permissões do usuário como dicionário, ex.:
    {
      'cad_usuarios': True,
      'cad_produtos': False,
      ...
    }
    Para cada permissão = True, cria um botão na sidebar.
    
    Retorna uma string com o nome da página clicada, ou None se nada foi clicado.
    """
    st.sidebar.title("Menu Lateral")

    # Vamos criar um mapeamento:
    # nome_interno -> (label_botao, funcao_da_pagina)
    # Assim, podemos adicionar 'Gerenciar_Usuarios' se ele for master ou tiver alguma permissão especial
    botoes = {}

    # Exemplo: se perm_cadastrar_usuarios == True => botão "Cadastrar Usuários"
    if perms.get("cadastrar_usuarios"):
        botoes["cad_usuarios"] = "Cadastrar Usuários"
        # Podemos também exibir "Gerenciar Usuários" se for master ou se decidir associar 
        # a mesma permissão. Fica a seu critério.
        botoes["gerenciar_usuarios"] = "Gerenciar Usuários"

    if perms.get("cadastrar_produtos"):
        botoes["cad_produtos"] = "Cadastrar Produtos"

    if perms.get("estornar_produtos"):
        botoes["estornar_produtos"] = "Estornar Produtos"

    if perms.get("emitir_venda"):
        botoes["emitir_venda"] = "Emitir Venda"

    if perms.get("financeiro"):
        botoes["financeiro"] = "Financeiro"

    # Sempre podemos ter "Minhas Permissões", se quiser
    # ou associar a uma permissão de "visualizar_permissoes".
    botoes["minhas_permissoes"] = "Minhas Permissões"

    # Também um botão de "Sair"
    botoes["sair"] = "Sair"

    pagina_clicada = None
    for key, label in botoes.items():
        if st.sidebar.button(label):
            pagina_clicada = key
    return pagina_clicada

##############################
# MAIN (Login + Navegação)
##############################

def main():
    st.title("Sistema de Login - Exemplo")

    criar_banco_de_dados()

    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
    if "usuario_logado" not in st.session_state:
        st.session_state.usuario_logado = ""
    if "permissoes" not in st.session_state:
        st.session_state.permissoes = {}

    if not st.session_state.autenticado:
        # Exibe formulário de login
        login_input = st.text_input("Login")
        senha_input = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            # Verifica se é Master
            if login_input == "Master" and senha_input == "1235":
                st.session_state.autenticado = True
                st.session_state.usuario_logado = "Master"
                # Define todas as permissões = True
                st.session_state.permissoes = {
                    'cadastrar_usuarios': True,
                    'cadastrar_produtos': True,
                    'estornar_produtos': True,
                    'emitir_venda': True,
                    'financeiro': True,
                }
                st.rerun()
            else:
                # Verifica no BD
                user_db = buscar_usuario_bd(login_input, senha_input)
                if user_db:
                    st.session_state.autenticado = True
                    st.session_state.usuario_logado = user_db[1]  # login
                    # user_db = (id, login, senha, perm1, perm2, perm3, perm4, perm5)
                    # Precisamos mapear para st.session_state.permissoes:
                    st.session_state.permissoes = {
                        'cadastrar_usuarios': bool(user_db[3]),
                        'cadastrar_produtos': bool(user_db[4]),
                        'estornar_produtos':  bool(user_db[5]),
                        'emitir_venda':      bool(user_db[6]),
                        'financeiro':        bool(user_db[7]),
                    }
                    st.rerun()
                else:
                    st.error("Login inválido.")
    else:
        # Já autenticado
        st.success(f"Bem-vindo, {st.session_state.usuario_logado}!")

        # Exibe menu lateral com base nas permissões
        pagina_clicada = exibir_menu_lateral(st.session_state.permissoes)
        
        if pagina_clicada:
            st.session_state["pagina_selecionada"] = pagina_clicada
        
        # Carrega a página que está selecionada
        pagina = st.session_state.get("pagina_selecionada", None)

        if pagina == "cad_usuarios":
            pagina_cadastrar_usuarios()
        elif pagina == "gerenciar_usuarios":
            pagina_gerenciar_usuarios()
        elif pagina == "cad_produtos":
            pagina_cadastrar_produtos()
        elif pagina == "estornar_produtos":
            pagina_estornar_produtos()
        elif pagina == "emitir_venda":
            pagina_emitir_venda()
        elif pagina == "financeiro":
            pagina_financeiro()
        elif pagina == "minhas_permissoes":
            pagina_minhas_permissoes()
        elif pagina == "sair":
            # Botão "Sair" -> deslogar
            st.session_state.autenticado = False
            st.session_state.usuario_logado = ""
            st.session_state.permissoes = {}
            st.session_state.pagina_selecionada = None
            st.rerun()
        else:
            # Nenhuma página selecionada ainda
            st.write("Selecione alguma opção no menu lateral.")

if __name__ == "__main__":
    main()
