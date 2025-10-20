# createZZ.py
import os
import re
import sys
import json
import sqlite3
import time

from encerrar_claim import encerrarClaiZO
from regex import R
from sympy import li

# ======= Força UTF-8 no stdout/stderr (evita UnicodeEncodeError em Windows) =======
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUTF8"] = "1"
if hasattr(sys.stdout, "reconfigure"): #Concluído
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# ======= Import do conector SAP (mantém sua estrutura de pastas) =======
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.connectSAP import conectar  # noqa: E402

def ok(payload=None): #Concluído
    """Imprime JSON de sucesso e sai com código 0."""
    print(json.dumps({"ok": True, "resultado": payload}, ensure_ascii=False))
    sys.exit(0)

def fail(msg, extra=None): #Concluído
    """Imprime JSON de erro e sai com código 1."""
    out = {"ok": False, "erro": str(msg)}
    if extra is not None:
        # garante string segura (sem objetos não serializáveis)
        out["detalhe"] = str(extra)
    print(json.dumps(out, ensure_ascii=False))
    sys.exit(1)

def get_db_path(): #Concluido
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    db_path = os.path.normpath(os.path.join(project_root, 'BD', 'banco_dados.db'))
    # opcional: garantir que a pasta exista
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return db_path

def verificaStatus(): #Em andamento

    DB_PATH = get_db_path()   
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor() 

    cursor.execute("""
    SELECT num_claimzz, qtdMedida
    FROM consultas_iqs9
    WHERE class_BU IS NOT NULL
        AND (
        num_claimzz IS NOT NULL
        OR (typeof(num_claimzz) = 'text' AND TRIM(num_claimzz) = '')
        )
    """)
    rows = cursor.fetchall()  # [(num_claimzz, qtdMedida), ...]
    conn.close()
    # num_claims   = [r[0] for r in rows]
    # qtd_medidas  = [r[1] for r in rows]
    if rows:
        session = conectar()

    for num_claim, qtd in rows:  # rows = [(num_claimzz, qtdMedida), ...]
        session.findById("wnd[0]/tbar[0]/okcd").text = "/nclm3"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/ctxtRIWO00-QMNUM").text = num_claim
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB11").select()
        qtdResp = 0
        for x in range (qtd):
            status = session.findById(f'wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB11/ssubSUB_GROUP_10:SAPLIQS0:7120/tblSAPLIQS0MASSNAHMEN_VIEWER/txtRIWO00-SMSTTXT[6,{x}]').text
            if status == "MEDE":
                qtdResp = qtdResp + 1     
        print(qtdResp)

        updateBD(num_claim, qtdResp)        
        if qtdResp == qtd:
            encerrarClaiZO()
    
    return  

def updateBD(num_claim, qtdResp): #Concluído

    DB_PATH = get_db_path()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE consultas_iqs9
        SET qtdFinalizada = ?
        WHERE num_claimzz = ?
          AND class_BU IS NOT NULL
    """, (qtdResp, num_claim))

    conn.commit()  # importante: salvar as alterações   
    conn.close()

    return

if __name__ == "__main__":#Concluído
    try:
        resultado = verificaStatus()
        ok(resultado)
    except Exception as e:
        # Devolve erro como JSON e exit code 1 (o Node responderá 500)
        fail("Falha ao criar ZZ", extra=repr(e))
