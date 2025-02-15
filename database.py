import sqlite3

def criar_banco_de_dados():
    """
    Cria (ou conecta) ao BD 'usuarios.db' e garante que a tabela 'usuarios' exista,
    sem a coluna 'perm_cadastrar_usuarios'.
    """
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()

    # Agora teremos 6 colunas de permissões:
    # perm_cadastrar_produtos, perm_estornar_produtos, perm_emitir_venda,
    # perm_financeiro, perm_gerenciar_usuarios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,

            perm_cadastrar_produtos  INTEGER DEFAULT 0,
            perm_estornar_produtos   INTEGER DEFAULT 0,
            perm_emitir_venda        INTEGER DEFAULT 0,
            perm_financeiro          INTEGER DEFAULT 0,
            perm_gerenciar_usuarios  INTEGER DEFAULT 0
        );
    """)

    conn.commit()
    conn.close()

def cadastrar_usuario_bd(login, senha,
                         perm_cadastrar_produtos,
                         perm_estornar_produtos,
                         perm_emit_venda,
                         perm_financeiro,
                         perm_gerenciar_usuarios):
    """
    Insere um novo usuário na tabela 'usuarios'. 
    Observação: não há 'perm_cadastrar_usuarios' mais.
    """
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO usuarios (
                login,
                senha,
                perm_cadastrar_produtos,
                perm_estornar_produtos,
                perm_emitir_venda,
                perm_financeiro,
                perm_gerenciar_usuarios
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            login,
            senha,
            int(perm_cadastrar_produtos),
            int(perm_estornar_produtos),
            int(perm_emit_venda),
            int(perm_financeiro),
            int(perm_gerenciar_usuarios)
        ))
        conn.commit()
    except sqlite3.IntegrityError:
        # Se cair aqui, significa que já existe um usuário com esse login
        conn.close()
        return False
    conn.close()
    return True

def listar_usuarios_bd():
    """
    Retorna todos os usuários (8 colunas):
      id, login, senha,
      perm_cadastrar_produtos,
      perm_estornar_produtos,
      perm_emitir_venda,
      perm_financeiro,
      perm_gerenciar_usuarios
    """
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            id,
            login,
            senha,
            perm_cadastrar_produtos,
            perm_estornar_produtos,
            perm_emitir_venda,
            perm_financeiro,
            perm_gerenciar_usuarios
        FROM usuarios
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def buscar_usuario_bd(login, senha):
    """
    Busca usuário pelo login e senha (8 colunas).
    """
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            id,
            login,
            senha,
            perm_cadastrar_produtos,
            perm_estornar_produtos,
            perm_emitir_venda,
            perm_financeiro,
            perm_gerenciar_usuarios
        FROM usuarios
        WHERE login = ? AND senha = ?
    """, (login, senha))
    row = cursor.fetchone()
    conn.close()
    return row

def atualizar_usuario_bd(user_id, nova_senha,
                         cad_produtos,
                         est_prod,
                         emit_venda,
                         financeiro,
                         gerenciar_usuarios):
    """
    Atualiza senha e permissões (8 colunas).
    """
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE usuarios
        SET senha = ?,
            perm_cadastrar_produtos  = ?,
            perm_estornar_produtos   = ?,
            perm_emitir_venda        = ?,
            perm_financeiro          = ?,
            perm_gerenciar_usuarios  = ?
        WHERE id = ?
    """, (
        nova_senha,
        int(cad_produtos),
        int(est_prod),
        int(emit_venda),
        int(financeiro),
        int(gerenciar_usuarios),
        user_id
    ))
    conn.commit()
    conn.close()

def excluir_usuario_bd(user_id):
    """Exclui um usuário pelo ID."""
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
