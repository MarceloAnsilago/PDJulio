# import streamlit as st

# def verificar_credenciais(usuario, senha):
#     return usuario == "Master" and senha == "1235"

# # Inicializa estados da sessão
# if 'autenticado' not in st.session_state:
#     st.session_state.autenticado = False
# if 'usuarios' not in st.session_state:
#     st.session_state.usuarios = {}

# if not st.session_state.autenticado:
#     with st.form("Login"):
#         st.header("Acesso Restrito")
#         usuario = st.text_input("Usuário Master")
#         senha = st.text_input("Senha", type="password")
        
#         if st.form_submit_button("Entrar"):
#             if verificar_credenciais(usuario, senha):
#                 st.session_state.autenticado = True
#                 st.rerun()
#             else:
#                 st.error("Credenciais inválidas")

# else:
#     st.success("✅ Autenticação bem-sucedida!")
#     st.header("Cadastro de Novos Usuários")
    
#     with st.form("Cadastro"):
#         novo_usuario = st.text_input("Novo Usuário")
        
#         # Seção de Permissões
#         st.subheader("Privilégios do Usuário")
#         col1, col2 = st.columns(2)
#         with col1:
#             perm_cadastrar_usuarios = st.checkbox("Cadastrar novos usuários")
#             perm_cadastrar_produtos = st.checkbox("Cadastrar produtos")
#             perm_estornar_produtos = st.checkbox("Estornar produtos")
#         with col2:
#             perm_emitir_venda = st.checkbox("Emitir Venda")
#             perm_financeiro = st.checkbox("Financeiro")
        
#         # Campos de senha
#         nova_senha = st.text_input("Nova Senha", type="password")
#         confirmar_senha = st.text_input("Confirmar Senha", type="password")
        
#         if st.form_submit_button("Cadastrar"):
#             if nova_senha != confirmar_senha:
#                 st.error("As senhas não coincidem")
#             elif novo_usuario in st.session_state.usuarios:
#                 st.error("Usuário já existe")
#             else:
#                 # Armazena usuário com permissões
#                 st.session_state.usuarios[novo_usuario] = {
#                     'senha': nova_senha,
#                     'permissoes': {
#                         'cadastrar_usuarios': perm_cadastrar_usuarios,
#                         'cadastrar_produtos': perm_cadastrar_produtos,
#                         'estornar_produtos': perm_estornar_produtos,
#                         'emitir_venda': perm_emitir_venda,
#                         'financeiro': perm_financeiro
#                     }
#                 }
#  
# 
# 
#                st.success(f"Usuário {novo_usuario} cadastrado com sucesso!")
import streamlit as st
from database import (
    criar_banco_de_dados,
    cadastrar_usuario_bd,
    buscar_usuario_bd,
    buscar_usuario_pelo_login_bd
)

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

        # Se não for Master, apenas exibe permissões
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
