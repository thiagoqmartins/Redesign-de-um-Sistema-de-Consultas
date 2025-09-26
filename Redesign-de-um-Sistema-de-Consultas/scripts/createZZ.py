# createZZ.py
import os
import re
import sys
import json
import sqlite3
import time

from regex import R
from sympy import li

# ======= Força UTF-8 no stdout/stderr (evita UnicodeEncodeError em Windows) =======
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUTF8"] = "1"
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# ======= Import do conector SAP (mantém sua estrutura de pastas) =======
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.connectSAP import conectar  # noqa: E402


# ======= Helpers de saída padronizada =======
def ok(payload=None):
    """Imprime JSON de sucesso e sai com código 0."""
    print(json.dumps({"ok": True, "resultado": payload}, ensure_ascii=False))
    sys.exit(0)


def fail(msg, extra=None):
    """Imprime JSON de erro e sai com código 1."""
    out = {"ok": False, "erro": str(msg)}
    if extra is not None:
        # garante string segura (sem objetos não serializáveis)
        out["detalhe"] = str(extra)
    print(json.dumps(out, ensure_ascii=False))
    sys.exit(1)


# ======= Lógica principal =======
def createZZ():

    conn = sqlite3.connect('BD/banco_dados.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM consultas_iqs9
        WHERE class_BU IS NOT NULL
        AND (num_claimzz IS NULL 
            OR (typeof(num_claimzz) = 'text' AND TRIM(num_claimzz) = ''))
    """)   

    linhas = cursor.fetchall() 

# tipo_nota TEXT, 0
# numero_nota TEXT, 1
# numero_ordem TEXT, 2
# cliente TEXT, 3
# nome_lista TEXT, 4
# descricao TEXT, 5
# texto_medida TEXT, 6
# inicio_desejado TEXT, 7
# fim_planejado TEXT, 8 
# fim_desejado TEXT, 9
# status TEXT, 10
# data_criacao TEXT, 11
# criado_por TEXT, 12
# notificador TEXT, 13
# num_claimzz INTERGER, 14
# status_claimZZ TEXT, 15
# seq_exec INTEGER, 16              
    
    for linha in linhas:      

        # descricao = linha[5]
        claim = linha[1]
        # conteudo = linha[17]

        session = conectar()

        conteudo, descricao, documentos = buscar_informacoes(session, claim)

        if not session:
            fail("Não foi possível conectar ao SAP (session=None).")
        
        # Navegação mínima para CLM1 e seleção do tipo ZZ
        session.findById("wnd[0]/tbar[0]/okcd").text = "/nclm1"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/cmbRIWO00-QMART").key = "ZZ"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB01/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_1:SAPLIQS0:7715/txtRIWO00-HEADKTXT").text = descricao  # class_bu
        session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB01/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPMCLAIM:7800/ctxtCLAIM-URGRP").text = "01"
        session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB01/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPMCLAIM:7800/ctxtCLAIM-URCOD").text = "0001"
        session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB01/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_1:SAPLIQS0:7715/cntlTEXT/shellcont/shell").text = "Claim (ZO) Origem: " + claim + "\n" + conteudo            
        session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB01/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPMCLAIM:7800/cmbVIQMEL-PRIOK").key = "1"
        session.findById("wnd[0]").sendVKey(0)

        #documentos

        session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB02").select()
        session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subBUTTON:SAPLCV140:0203/radGF_ALLE").select()
        session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subDOC_ALV:SAPLCV140:0207/tblSAPLCV140SUB_DOC/ctxtDRAW-DOKAR[0,0]").text = documentos[0]
        session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subDOC_ALV:SAPLCV140:0207/tblSAPLCV140SUB_DOC/ctxtDRAW-DOKNR[1,0]").text = "10013589049"
        session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subDOC_ALV:SAPLCV140:0207/tblSAPLCV140SUB_DOC/ctxtDRAW-DOKTL[2,0]").text = "000"
        session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subDOC_ALV:SAPLCV140:0207/tblSAPLCV140SUB_DOC/ctxtDRAW-DOKVR[3,0]").text = "03"

        
        # Se chegou aqui sem exceções, consideramos sucesso
    #    return "Concluído"
    conn.close() 
    return "Concluído"

def buscar_informacoes(session, numero_nota):
    documentos = []   
    i = 0
    session.findById("wnd[0]").maximize()
    session.findById("wnd[0]/tbar[0]/okcd").text = "/nclm3"
    session.findById("wnd[0]").sendVKey(0)
    session.findById("wnd[0]/usr/ctxtRIWO00-QMNUM").text = numero_nota
    session.findById("wnd[0]").sendVKey(0)

    conteudo_claim = session.FindById(r"wnd[0]/usr/tabsTAB_GROUP_10/tabp10\TAB01/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_1:SAPLIQS0:7715/cntlTEXT/shellcont/shell").text
    conteudo_claim = "\n".join(conteudo_claim.splitlines()[1:])    
    descricao = session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB01/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_1:SAPLIQS0:7715/txtRIWO00-HEADKTXT").text

    #buscar documentos
    session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB02").select()  
    session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subBUTTON:SAPLCV140:0203/radGF_ALLE").select()

    while True:
        try:            
            valor = session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subDOC_ALV:SAPLCV140:0207/tblSAPLCV140SUB_DOC/ctxtDRAW-DOKAR[0,0]").text

            if valor == "":   # condição de parada → célula vazia
                break
            documentos.append(valor)
            session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subDOC_ALV:SAPLCV140:0207/tblSAPLCV140SUB_DOC").verticalScrollbar.position = 1
            i += 1

        except:
            break
    
    return conteudo_claim, descricao, documentos

if __name__ == "__main__":
    try:
        resultado = createZZ()
        ok(resultado)
    except Exception as e:
        # Devolve erro como JSON e exit code 1 (o Node responderá 500)
        fail("Falha ao criar ZZ", extra=repr(e))
