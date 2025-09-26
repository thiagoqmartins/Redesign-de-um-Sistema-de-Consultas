# import sys
# import json
# import sqlite3
# import os

# def atualizar_ordem(entrada_json):
#     dados = json.loads(entrada_json)
#     nova_ordem = dados.get("novaOrdem", [])

#     print(json.dumps(nova_ordem, indent=2), file=sys.stderr)

#     db_path = os.path.join(os.path.dirname(__file__), '..', 'BD', 'banco_dados.db')
#     conn = sqlite3.connect(db_path)
#     cursor = conn.cursor()

#     try:
#         cursor.execute("BEGIN TRANSACTION")
#         for item in nova_ordem:
#             numero = item["numero_nota"]
#             nova_seq = item["nova_seq_exec"]
#             cursor.execute("UPDATE consultas_iqs9 SET seq_exec = ? WHERE numero_nota = ?", (nova_seq, numero))
#         conn.commit()       
#         print(json.dumps({"status": "ok"}))
#     except Exception as e:
#         conn.rollback()
#         print(json.dumps({"status": "erro", "mensagem": str(e)}))
#         sys.exit(1)
#     finally:
#         conn.close()

# if __name__ == "__main__":
#     entrada_json = sys.stdin.read()
#     atualizar_ordem(entrada_json)

import sys
import json
import sqlite3
import os

def atualizar_ordem(entrada_json):
    print("🔧 Script Python iniciado", file=sys.stderr)

    try:
        dados = json.loads(entrada_json)
        nova_ordem = dados.get("novaOrdem", [])
        print(f"📦 novaOrdem recebida com {len(nova_ordem)} itens", file=sys.stderr)
    except Exception as e:
        print(f"❌ Erro ao carregar JSON: {e}", file=sys.stderr)
        print(json.dumps({"status": "erro", "mensagem": "JSON inválido"}))
        sys.exit(1)

    db_path = os.path.join(os.path.dirname(__file__), '..', 'BD', 'banco_dados.db')
    print(f"🗂️ Caminho do banco: {db_path}", file=sys.stderr)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("BEGIN TRANSACTION")
        for item in nova_ordem:
            numero = item["numero_nota"]
            nova_seq = item["nova_seq_exec"]
            print(f"🔄 Atualizando numero_nota={numero} para seq_exec={nova_seq}", file=sys.stderr)
            cursor.execute("UPDATE consultas_iqs9 SET seq_exec = ? WHERE numero_nota = ?", (nova_seq, numero))
        conn.commit()
        print("✅ Commit realizado com sucesso", file=sys.stderr)
        print(json.dumps({"status": "ok"}))
    except Exception as e:
        conn.rollback()
        print(f"❌ Erro durante UPDATE: {e}", file=sys.stderr)
        print(json.dumps({"status": "erro", "mensagem": str(e)}))
        sys.exit(1)
    finally:
        conn.close()
        print("🔚 Conexão com banco encerrada", file=sys.stderr)

if __name__ == "__main__":
    print("📨 Aguardando dados via stdin...", file=sys.stderr)
    entrada_json = sys.stdin.read()
    print("📬 Dados recebidos", file=sys.stderr)
    atualizar_ordem(entrada_json)
