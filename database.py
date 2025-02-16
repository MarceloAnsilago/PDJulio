import sqlite3

def criar_banco_de_dados():
    """
    Cria (ou conecta) ao BD 'usuarios.db' e garante que as tabelas 'usuarios', 'produtos'
    e 'movimentos' existam.
    """
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()

    # Tabela de USUÁRIOS (sem a coluna perm_cadastrar_produtos)
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

    # Tabela de MOVIMENTOS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            nome TEXT NOT NULL,
            custo_inicial REAL NOT NULL,
            preco_venda REAL NOT NULL,
            quantidade INTEGER NOT NULL,
            tipo TEXT NOT NULL,              -- 'entrada' ou 'saída'
            usuario TEXT NOT NULL,
            metodo_pagamento TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Ativo',
            total REAL NOT NULL
        );
    """)

    conn.commit()
    conn.close()

# ----------------------------
# Funções para USUÁRIOS
# ----------------------------

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
    Atualiza senha e permissões (8 colunas) do usuário.
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

# ----------------------------
# Funções para PRODUTOS
# ----------------------------

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
    return produto_id

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
    """Exclui um produto definitivamente da tabela."""
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
    conn.commit()
    conn.close()

# ----------------------------
# Funções para MOVIMENTOS
# ----------------------------

def criar_tabela_movimentos():
    """
    Cria (ou conecta) ao BD 'usuarios.db' e garante que a tabela 'movimentos' exista.
    Essa tabela registra as movimentações (entrada ou saída) de produtos.
    """
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            nome TEXT NOT NULL,
            custo_inicial REAL NOT NULL,
            preco_venda REAL NOT NULL,
            quantidade INTEGER NOT NULL,
            tipo TEXT NOT NULL,              -- 'entrada' ou 'saída'
            usuario TEXT NOT NULL,
            metodo_pagamento TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Ativo',
            total REAL NOT NULL
        );
    """)
    conn.commit()
    conn.close()

def cadastrar_movimentacao(produto_nome, custo_inicial, preco_venda, quantidade,
                           tipo, usuario, metodo_pagamento, status="Ativo"):
    """
    Insere uma nova movimentação na tabela 'movimentos'.
    Calcula o total (quantidade * custo_inicial) e registra a data atual.
    """
    import datetime
    total = quantidade * custo_inicial  # Total calculado com base no custo inicial
    data = datetime.datetime.now().isoformat(sep=" ", timespec="seconds")
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO movimentos (
            data, nome, custo_inicial, preco_venda, quantidade,
            tipo, usuario, metodo_pagamento, status, total
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (data, produto_nome, custo_inicial, preco_venda, quantidade,
          tipo, usuario, metodo_pagamento, status, total))
    conn.commit()
    conn.close()

def listar_movimentacoes_bd():
    """
    Retorna todas as movimentações cadastradas.
    """
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, data, nome, custo_inicial, preco_venda, quantidade,
               tipo, usuario, metodo_pagamento, status, total
        FROM movimentos
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows
