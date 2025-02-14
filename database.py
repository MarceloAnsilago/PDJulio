import sqlite3

def criar_banco_de_dados():
    """Cria (ou conecta) ao BD 'usuarios.db' e garante que a tabela 'usuarios' exista."""
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            perm_cadastrar_usuarios INTEGER DEFAULT 0,
            perm_cadastrar_produtos INTEGER DEFAULT 0,
            perm_estornar_produtos  INTEGER DEFAULT 0,
            perm_emitir_venda       INTEGER DEFAULT 0,
            perm_financeiro         INTEGER DEFAULT 0
        );
    """)
    conn.commit()
    conn.close()

def cadastrar_usuario_bd(login, senha,
                         perm_cadastrar_usuarios,
                         perm_cadastrar_produtos,
                         perm_estornar_produtos,
                         perm_emitir_venda,
                         perm_financeiro):
    """Insere um novo usuário na tabela 'usuarios'. Retorna True se deu certo, False se já existe."""
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO usuarios
            (login, senha, perm_cadastrar_usuarios, perm_cadastrar_produtos, 
             perm_estornar_produtos, perm_emitir_venda, perm_financeiro) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            login, 
            senha,
            int(perm_cadastrar_usuarios),
            int(perm_cadastrar_produtos),
            int(perm_estornar_produtos),
            int(perm_emitir_venda),
            int(perm_financeiro)
        ))
        conn.commit()
    except sqlite3.IntegrityError:
        # Se cair aqui, significa que já existe um usuário com o mesmo login
        conn.close()
        return False
    conn.close()
    return True

def buscar_usuario_bd(login, senha):
    """Busca usuário pelo login e senha. Retorna a linha do BD ou None se não encontrar."""
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM usuarios WHERE login = ? AND senha = ?", (login, senha))
    row = cursor.fetchone()
    
    conn.close()
    return row

def buscar_usuario_pelo_login_bd(login):
    """Busca usuário pelo login (independente da senha)."""
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM usuarios WHERE login = ?", (login,))
    row = cursor.fetchone()
    
    conn.close()
    return row
