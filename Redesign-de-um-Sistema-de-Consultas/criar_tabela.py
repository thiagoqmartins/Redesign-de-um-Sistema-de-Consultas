import sqlite3
import os

# Caminho do banco de dados
caminho_db = os.path.join(os.path.dirname(__file__), 'BD', 'banco_dados.db')

# Conecta ao banco
conexao = sqlite3.connect(caminho_db)
cursor = conexao.cursor()

# Cria uma nova tabela chamada 'usuarios'
cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        usuario TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        data_criacao TEXT DEFAULT CURRENT_TIMESTAMP
    )
''')

# Salva e fecha
conexao.commit()
conexao.close()

