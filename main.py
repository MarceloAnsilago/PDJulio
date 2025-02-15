import streamlit as st
import pandas as pd

from database import (
    criar_banco_de_dados,
    cadastrar_usuario_bd,
    buscar_usuario_bd,
    buscar_usuario_pelo_login_bd,
    listar_usuarios_bd,
    excluir_usuario_bd,
    atualizar_usuario_bd
)

def gerenciar_usuarios():
    """Lista todos os usuários em uma tabela e permite editar ou excluir."""
    st.subheader("Gerenciar Usuários")
    usuarios = listar_usuarios_bd()
    
    if not usuarios:
        st.info("Nenhum usuário cadastrado.")
        return
    
    # Converte para DataFrame para exibir em tabela
    colunas = [
        "id", 
        "login", 
        "senha",
        "perm_cadastrar_usuarios", 
        "perm_cadastrar_produtos",
        "perm_estornar_produtos", 
        "perm_emitir_venda",
        "perm_financeiro"
    ]
    df = pd.DataFrame(usuarios, columns=colunas)
    st.dataframe(df, use_container_width=True)

    # Cria um selectbox para escolher qual usuário gerenciar
    opcoes = [f"{u[0]} - {u[1]}" for u in usuarios]  # "id - login"
    escolha = st.selectbox("Selecione um usuário para Editar ou Excluir:", opcoes)
    
    if escolha:
        # Extrai o ID da escolha (tudo antes do ' - ')
        user_id = int(escolha.split(' - ')[0])
        
        # Busca o usuário nos dados
        user_info = next((u for u in usuarios if u[0] == user_id), None)
        if user_info:
            (id_, login_, senha_, 
             perm_cad_usr, perm_cad_prod, 
             perm_est_prod, perm_emit_venda, perm_fin) = user_info
            
            st.write(f"**Editando usuário:** {login_} (ID={id_})")
            
            # Formulário de edição
            with st.form("editar_usuario"):
                nova_senha = st.text_input(
                    "Nova Senha (deixar em branco para não alterar)", 
                    type="password"
                )
                perm_cad_usuarios_edit = st.checkbox("Cadastrar Usuários", value=bool(perm_cad_usr))
                perm_cad_produtos_edit = st.checkbox("Cadastrar Produtos", value=bool(perm_cad_prod))
                perm_est_prod_edit     = st.checkbox("Estornar Produtos", value=bool(perm_est_prod))
                perm_emit_venda_edit   = st.checkbox("Emitir Venda", value=bool(perm_emit_venda))
                perm_financeiro_edit   = st.checkbox("Financeiro", value=bool(perm_fin))

                if st.form_submit_button("Salvar Alterações"):
                    # Se a nova_senha estiver vazia, mantenha a senha anterior
                    if not nova_senha:
                        nova_senha = senha_  
                    
                    atualizar_usuario_bd(
                        id_,
                        nova_senha,
                        perm_cad_usuarios_edit,
                        perm_cad_produtos_edit,
                        perm_est_prod_edit,
                        perm_emit_venda_edit,
                        perm_financeiro_edit
                    )
                    st.success(f"Usuário '{login_}' atualizado com sucesso!")
                    st.rerun()

            # Botão para excluir
            if st.button("Excluir Usuário"):
                excluir_usuario_bd(id_)
                st.warning(f"Usuário '{login_}' excluído!")
                st.rerun()

def main():
    st.title("Sistema de Login - Exemplo")
    
    # Cria ou conecta ao banco e garante que a tabela exista
    criar_banco_de_dados()

    # Usamos st.session_state para controlar a autenticação
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
    if "usuario_logado" not in st.session_state:
        st.session_state.usuario_logado = ""

    # Se não estiver autenticado, exibe formulário de login
    if not st.session_state.autenticado:
        login_input = st.text_input("Login")
        senha_input = st.text_input("Senha", type="password")
        
        if st.button("Entrar"):
            # Verifica se é Master
            if login_input == "Master" and senha_input == "1235":
                st.session_state.autenticado = True
                st.session_state.usuario_logado = "Master"
                st.rerun()  # recarrega a página

            else:
                # Caso não seja Master, verifica no banco de dados
                user_db = buscar_usuario_bd(login_input, senha_input)
                if user_db:
                    st.session_state.autenticado = True
                    st.session_state.usuario_logado = login_input
                    st.rerun()
                else:
                    st.error("Login inválido.")

    else:
        # Se já estiver autenticado
        st.success(f"Bem-vindo, {st.session_state.usuario_logado}!")

        # Lógica específica para Master
        if st.session_state.usuario_logado == "Master":
            st.header("Cadastrar Novo Usuário")

            with st.form("cadastro"):
                novo_login = st.text_input("Novo Login")
                nova_senha = st.text_input("Nova Senha", type="password")

                st.subheader("Permissões")
                perm_cad_usuarios = st.checkbox("Cadastrar Usuários")
                perm_cad_produtos = st.checkbox("Cadastrar Produtos")
                perm_est_prod     = st.checkbox("Estornar Produtos")
                perm_emit_venda   = st.checkbox("Emitir Venda")
                perm_financeiro   = st.checkbox("Financeiro")

                if st.form_submit_button("Cadastrar"):
                    # Tenta inserir no banco
                    sucesso = cadastrar_usuario_bd(
                        novo_login,
                        nova_senha,
                        perm_cad_usuarios,
                        perm_cad_produtos,
                        perm_est_prod,
                        perm_emit_venda,
                        perm_financeiro
                    )
                    if sucesso:
                        st.success(f"Usuário '{novo_login}' cadastrado com sucesso!")
                    else:
                        st.error(f"Não foi possível cadastrar. Usuário '{novo_login}' já existe!")

            # Divisão
            st.write("---")
            st.header("Gerenciar Usuários Existentes")
            gerenciar_usuarios()

        # Se não for Master, apenas exibe permissões do usuário logado
        else:
            st.header("Minhas Permissões")
            user_info = buscar_usuario_pelo_login_bd(st.session_state.usuario_logado)
            if user_info:
                # user_info = (id, login, senha, perm_cadastrar_usuarios, perm_cadastrar_produtos, etc...)
                (
                    _id, _login, _senha,
                    perm_cad_usr, perm_cad_prod,
                    perm_est_prod, perm_emit_venda, perm_fin
                ) = user_info

                st.write(f"• Cadastrar Usuários: **{bool(perm_cad_usr)}**")
                st.write(f"• Cadastrar Produtos: **{bool(perm_cad_prod)}**")
                st.write(f"• Estornar Produtos: **{bool(perm_est_prod)}**")
                st.write(f"• Emitir Venda: **{bool(perm_emit_venda)}**")
                st.write(f"• Financeiro: **{bool(perm_fin)}**")
            else:
                st.error("Usuário não encontrado no banco de dados.")

if __name__ == "__main__":
    main()
