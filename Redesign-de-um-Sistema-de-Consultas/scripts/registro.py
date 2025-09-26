import sqlite3
import os
import bcrypt
import sys
import json

def executar(*args):
    caminho_db = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'BD', 'banco_dados.db'))
    
    try:
        nome = args[0]
        usuario = args[1]
        email = args[2]
        senha_plana = args[3]
        nivel_acesso = 0
        status = 2

        # ============================
        # NÍVEL DE ACESSO (nivel_acesso)
        # ============================
        # 0 - User: acesso limitado; pode usar funcionalidades básicas da plataforma.
        # 1 - Moderador: pode revisar e gerenciar conteúdos de outros usuários.
        # 2 - Admin: tem permissões administrativas amplas, como gerenciar usuários, conteúdo e configurações.
        # 3 - Super_Admin: acesso total ao sistema; pode alterar permissões de outros admins, realizar manutenções críticas e visualizar logs sensíveis.
        # 4 - Virtual_User: conta automatizada usada por processos do sistema ou integrações.  

        # ============================
        # STATUS DO USUÁRIO (status)
        # ============================
        # 0 - Inativo: conta criada, mas atualmente desativada; o usuário não pode fazer login.
        # 1 - Ativo: conta plenamente funcional e com acesso autorizado.
        # 2 - Pendente: conta aguardando ativação manual ou confirmação de e-mail.
        # 3 - Suspenso: acesso temporariamente bloqueado.   
           


        # Gera hash da senha
        senha_hash = bcrypt.hashpw(senha_plana.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Conecta ao banco
        conexao = sqlite3.connect(caminho_db)
        cursor = conexao.cursor()

        # Cria tabela se não existir (opcional)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                usuario TEXT,
                email TEXT,
                senha TEXT,
                nivel_acesso INTEGER,
                status INTEGER
            )
        ''')

        # Insere dados
        cursor.execute('''
            INSERT INTO usuarios (nome, usuario, email, senha, nivel_acesso, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (nome, usuario, email, senha_hash, nivel_acesso, status))

        conexao.commit()
        resultado = ["ok"]
        print(json.dumps(resultado))

    except Exception as e:
        resultado = str(e)
        print(json.dumps(resultado))

    finally:
        try:
            conexao.close()
        except:
            pass

def validar(*args):
    caminho_db = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'BD', 'banco_dados.db'))

    try:
        usuario = args[0]
        senha_plana = args[1]

        conexao = sqlite3.connect(caminho_db)
        cursor = conexao.cursor()

        cursor.execute('SELECT senha, status, nivel_acesso, usuario FROM usuarios WHERE usuario = ?', (usuario,))
        resultado = cursor.fetchone()
        if resultado:
            senha_hash, status, nivel_acesso, usuario_bd = resultado 
                                   
        else:
            print(json.dumps({"error": "Ops! Nome de usuário não encontrado!"}))
            return
        
        if resultado:                        
            senha_hash, status, nivel_acesso, usuario_bd = resultado        
            if status != 1:  # Apenas usuários ativos (status 1)
                mensagens_status = {
                    0: "Conta inativa. Contate o administrador.",
                    2: "Conta pendente de ativação.",
                    3: "Conta suspensa temporariamente.",
                    }
                mensagem_erro = mensagens_status.get(status, "Status de conta desconhecido.")
                print(json.dumps({ "success": False, "error": mensagem_erro }))
                # print(json.dumps({"sucess": False, "error": status}))
                return

            if bcrypt.checkpw(senha_plana.encode('utf-8'), senha_hash.encode('utf-8')):
                print(json.dumps({ "success": True, "nivel_acesso": nivel_acesso }))
                return
        senha_hash, status, nivel_acesso, usuario = resultado
        # print(json.dumps({"Usuario Encontrado:": usuario }))
        print(json.dumps({"error": "Ops! Parece que a senha está incorreta. Tente novamente." }))

    except Exception as e:
        print(json.dumps({ "success": False, "error": str(e) }))
        return

    finally:
        try:
            conexao.close()
        except:
            pass


# ==== Seletor de função ====
if __name__ == "__main__":
    acao = sys.argv[1]

    if acao == "executar":
        executar(*sys.argv[2:])
    elif acao == "validar":
        validar(*sys.argv[2:])
    else:
        print(json.dumps({ "success": False, "error": "Ação inválida" }))