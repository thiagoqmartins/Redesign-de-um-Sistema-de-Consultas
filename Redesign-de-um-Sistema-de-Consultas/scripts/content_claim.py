import sys
import os
import sqlite3
import win32com.client

# Garante o caminho para os imports funcionarem
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.connectSAP import conectar

# Força UTF-8 no terminal do Windows
sys.stdout.reconfigure(encoding='utf-8')

def dados_claim(): 
    session = conectar()

    # Caminho absoluto para o banco de dados
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    db_path = os.path.join(base_dir, 'BD', 'banco_dados.db')

    # Cria a pasta BD se não existir
    os.makedirs(os.path.join(base_dir, 'BD'), exist_ok=True)

    # Conecta ao banco
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT numero_nota FROM consultas_iqs9
        WHERE content IS NULL OR TRIM(content) = ''
    """)

    notas_vazias = cursor.fetchall()

    for row in notas_vazias:
        numero_nota = row[0]  
        session.findById("wnd[0]").maximize()
        session.findById("wnd[0]/tbar[0]/okcd").text = "/nclm3"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/ctxtRIWO00-QMNUM").text = numero_nota
        session.findById("wnd[0]").sendVKey(0)

        conteudo_claim = session.FindById(r"wnd[0]/usr/tabsTAB_GROUP_10/tabp10\TAB01/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_1:SAPLIQS0:7715/cntlTEXT/shellcont/shell").text
        conteudo_claim = "\n".join(conteudo_claim.splitlines()[1:])          

        cursor.execute("""
            UPDATE consultas_iqs9
            SET content = ?
            WHERE numero_nota = ?        
        """, (conteudo_claim, numero_nota))

        conn.commit()

    conn.close()
    return "Concluído"

if __name__ == "__main__":
    x = dados_claim()
    print(x)
