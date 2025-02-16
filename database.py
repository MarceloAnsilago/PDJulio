import sqlite3

def criar_banco_de_dados():
    """
    Cria (ou conecta) ao BD 'usuarios.db' e garante que as tabelas 'usuarios' e 'produtos' existam.
    """
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()

    # Tabela de USUÁRIOS
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

    # Tabela de PRODUTOS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE NOT NULL,
            info_complementar TEXT,
            status TEXT NOT NULL DEFAULT 'Ativo',
            preco REAL NOT NULL DEFAULT 0
        );
    """)

    conn.commit()
    conn.close()

# ------------------------------------------------
# USUÁRIOS
# ------------------------------------------------

def cadastrar_usuario_bd(login, senha,
                         perm_cadastrar_produtos,
                         perm_estornar_produtos,
                         perm_emitir_venda,
                         perm_financeiro,
                         perm_gerenciar_usuarios):
    """
    Insere um novo usuário na tabela 'usuarios'. 
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
            int(perm_emitir_venda),
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

# ------------------------------------------------
# PRODUTOS
# ------------------------------------------------

def cadastrar_produto_bd(nome, info, status, preco):
    """Insere um produto na tabela 'produtos'."""
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO produtos (nome, info_complementar, status, preco)
            VALUES (?, ?, ?, ?)
        """, (nome, info, status, preco))
        conn.commit()
        produto_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        conn.close()
        return False
    conn.close()
    return produto_id  # Retorna o ID do novo produto

def listar_produtos_bd():
    """Retorna todos os produtos cadastrados."""
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, nome, info_complementar, status, preco
        FROM produtos
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def atualizar_produto_bd(produto_id, novo_nome, nova_info, novo_status, novo_preco):
    """Atualiza os dados de um produto."""
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE produtos
        SET nome = ?,
            info_complementar = ?,
            status = ?,
            preco = ?
        WHERE id = ?
    """, (novo_nome, nova_info, novo_status, novo_preco, produto_id))
    conn.commit()
    conn.close()

def excluir_produto_bd(produto_id):
    """Exclui um produto definitivamente da tabela (ou poderia inativar)."""
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
    conn.commit()
    conn.close()
