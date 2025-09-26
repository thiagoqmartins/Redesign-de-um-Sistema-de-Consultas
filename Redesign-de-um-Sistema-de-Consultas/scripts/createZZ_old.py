# createZZ.py
import os
import sys
import json
import sqlite3
import time

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
    """
    Abre sessão SAP e cria uma claim do tipo ZZ de forma mínima.
    Retorna string de confirmação em caso de sucesso.
    """
    session = conectar()
    if not session:
        fail("Não foi possível conectar ao SAP (session=None).")

    # Navegação mínima para CLM1 e seleção do tipo ZZ
    session.findById("wnd[0]/tbar[0]/okcd").text = "/nclm1"
    session.findById("wnd[0]").sendVKey(0)
    session.findById("wnd[0]/usr/cmbRIWO00-QMART").key = "ZZ"
    session.findById("wnd[0]").sendVKey(0)

    # Se chegou aqui sem exceções, consideramos sucesso
    return "Concluído"


def criar_banco_e_inserir_dados(lista_de_dados, session):
    # Conectar ou criar banco
    conn = sqlite3.connect('BD/banco_dados.db')
    cursor = conn.cursor()

    # Criar tabela (se não existir) com chave composta
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS consultas_iqs9 (
            tipo_nota TEXT,
            numero_nota TEXT,
            numero_ordem TEXT,
            cliente TEXT,
            nome_lista TEXT,
            descricao TEXT,
            texto_medida TEXT,
            inicio_desejado TEXT,
            fim_planejado TEXT,
            fim_desejado TEXT,
            status TEXT,
            data_criacao TEXT,
            criado_por TEXT,
            notificador TEXT,
            num_claimzz INTERGER,
            status_claimZZ TEXT,
            seq_exec INTEGER,              
            PRIMARY KEY (numero_nota, numero_ordem)
        )
    ''') 

    # Inserção dos dados
    for dado in lista_de_dados:
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO consultas_iqs9 (
                    tipo_nota, numero_nota, numero_ordem, cliente, nome_lista, descricao, 
                    texto_medida, inicio_desejado, fim_planejado, fim_desejado, status, 
                    data_criacao, criado_por, notificador, seq_exec
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                dado["tipo_nota"],
                dado["numero_nota"],
                dado["numero_ordem"],
                dado["cliente"],
                dado["nome_lista"],
                dado["descricao"],
                dado["texto_medida"],
                dado["inicio_desejado"],
                dado["fim_planejado"],
                dado["fim_desejado"],
                dado["status"],
                dado["data_criacao"],
                dado["criado_por"],
                dado["notificador"],  
                dado["sequencia"]              
            ))
            # if cursor.rowcount == 1:
            #     buscar_dados(session=session, nota=dado["numero_nota"])                        
        except Exception as e:
            print(f"Erro ao inserir registro Nota: {dado['numero_nota']} Ordem: {dado['numero_ordem']} -> {e}")
    conn.commit()
    conn.close()


if __name__ == "__main__":
    try:
        resultado = createZZ()
        ok(resultado)
    except Exception as e:
        # Devolve erro como JSON e exit code 1 (o Node responderá 500)
        fail("Falha ao criar ZZ", extra=repr(e))





# import sqlite3
# import os
# import json
# import time
# import sys

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# from scripts.connectSAP import conectar

# # from transacoes import trans_clm3

#      #     tipo_nota TEXT,
#         #     numero_nota TEXT,
#         #     numero_ordem TEXT,
#         #     cliente TEXT,
#         #     nome_lista TEXT,
#         #     descricao TEXT,
#         #     texto_medida TEXT,
#         #     inicio_desejado TEXT,
#         #     fim_planejado TEXT,
#         #     fim_desejado TEXT,
#         #     status TEXT,
#         #     data_criacao TEXT,
#         #     criado_por TEXT,
#         #     notificador TEXT,
#         #     claim_zz TEXT,       
#         #     PRIMARY KEY (numero_nota, numero_ordem)

# # def buscar_dados(session):  

# #     conn = sqlite3.connect('BD/banco_dados.db')
# #     cursor = conn.cursor()
# #     cursor.execute("SELECT numero_nota FROM consultas_iqs9 WHERE claim_zz = 'N'")

# #     resultados = cursor.fetchall()

# #     for linha in resultados:
# #         nota = linha[0]          
# #         session.findById("wnd[0]/tbar[0]/okcd").text = "/nclm3"
# #         session.findById("wnd[0]").sendVKey(0)
# #         session.findById("wnd[0]/usr/ctxtRIWO00-QMNUM").text = nota
# #         session.findById("wnd[0]").sendVKey(0)
# #         a = session.findByID("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB01/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_1:SAPLIQS0:7715/txtRIWO00-HEADKTXT").text
# #         # createZZ(session, a)
 
# #     return "Concluído"   

# def createZZ():
# #  desc, txtSolic, nDoc ):   
#     # nMed = 0  
#     session = conectar()

#     session.findById("wnd[0]/tbar[0]/okcd").text = "/nclm1"
#     session.findById("wnd[0]").sendVKey(0)
#     session.findById("wnd[0]/usr/cmbRIWO00-QMART").key = "ZZ"
#     session.findById("wnd[0]").sendVKey(0)      
#     # time.sleep(160)
#     return ("Concluido")
#     # session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB01/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_1:SAPLIQS0:7715/txtRIWO00-HEADKTXT").caretPosition = 17
#     # session.findById("wnd[0]").sendVKey(0)
#     # session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB01/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_1:SAPLIQS0:7715/cntlTEXT/shellcont/shell").text = textoSintese
    
#     # time.sleep(160)
#     # session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\TAB01/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_1:SAPLIQS0:7715/cntlTEXT/shellcont/shell").setSelectionIndexes(24, 24)
#     # session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\TAB01/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPMCLAIM:7800/ctxtCLAIM-URGRP").setFocus()
#     # session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\TAB01/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPMCLAIM:7800/ctxtCLAIM-URGRP").caretPosition = 0
#     # session.findById("wnd[0]").sendVKey(4)
#     # session.findById("wnd[1]/usr/cntlTREE_CONTROL_AREA/shellcont/shell").expandNode("          2")
#     # session.findById("wnd[1]/usr/cntlTREE_CONTROL_AREA/shellcont/shell").topNode = "          1"
#     # session.findById("wnd[1]/usr/cntlTREE_CONTROL_AREA/shellcont/shell").selectItem("          3", "3")
#     # session.findById("wnd[1]/usr/cntlTREE_CONTROL_AREA/shellcont/shell").ensureVisibleHorizontalItem("          3", "3")
#     # session.findById("wnd[1]/usr/cntlTREE_CONTROL_AREA/shellcont/shell").doubleClickItem("          3", "3")
#     # session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\TAB01/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPMCLAIM:7800/cmbVIQMEL-PRIOK").key = "1"
#     # session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\TAB01/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPMCLAIM:7800/ctxtVIQMEL-STRUR").setFocus()
#     # session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\TAB01/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPMCLAIM:7800/ctxtVIQMEL-STRUR").caretPosition = 5
#     # session.findById("wnd[0]").sendVKey(0)
#     # session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\TAB01/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_1:SAPLIQS0:7715/cntlTEXT/shellcont/shell").text = "COLAR TEXTO SOLICITAÇÃO\r\r"
#     # session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\TAB01/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_1:SAPLIQS0:7715/cntlTEXT/shellcont/shell").setSelectionIndexes(24, 24)
#     # session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\TAB02").select()
#     # session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\TAB01").select()
#     # session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\TAB01/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_1:SAPLIQS0:7715/cntlTEXT/shellcont/shell").setUnprotectedTextPart(0, "COLAR TEXTO SOLICITAÇÃO\rKLÇ\r~KLP\r´\r")
#     # session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\TAB01/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_1:SAPLIQS0:7715/cntlTEXT/shellcont/shell").setSelectionIndexes(102, 102)
#     # session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\TAB02").select()
#     # session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subBUTTON:SAPLCV140:0203/radGF_ALLE").setFocus()
#     # session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subBUTTON:SAPLCV140:0203/radGF_ALLE").select()
#     # session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subDOC_ALV:SAPLCV140:0207/tblSAPLCV140SUB_DOC/ctxtDRAW-DOKAR[0,0]").text = "ZFE"
#     # session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subDOC_ALV:SAPLCV140:0207/tblSAPLCV140SUB_DOC/ctxtDRAW-DOKNR[1,0]").text = "1234567892"
#     # session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subDOC_ALV:SAPLCV140:0207/tblSAPLCV140SUB_DOC/ctxtDRAW-DOKTL[2,0]").text = "000"
#     # session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subDOC_ALV:SAPLCV140:0207/tblSAPLCV140SUB_DOC/ctxtDRAW-DOKVR[3,0]").text = "01"
#     # session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subDOC_ALV:SAPLCV140:0207/tblSAPLCV140SUB_DOC/ctxtDRAW-DOKAR[0,1]").setFocus()
#     # session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subDOC_ALV:SAPLCV140:0207/tblSAPLCV140SUB_DOC/ctxtDRAW-DOKAR[0,1]").caretPosition = 0
#     # session.findById("wnd[0]").sendVKey(0)
#     # session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\TAB17").select()
#     # session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subDOC_ALV:SAPLCV140:0207/tblSAPLCV140SUB_DOC/ctxtDRAW-DOKAR[0,0]").text = ""
#     # session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subDOC_ALV:SAPLCV140:0207/tblSAPLCV140SUB_DOC/ctxtDRAW-DOKNR[1,0]").text = ""
#     # session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subDOC_ALV:SAPLCV140:0207/tblSAPLCV140SUB_DOC/ctxtDRAW-DOKTL[2,0]").text = ""
#     # session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subDOC_ALV:SAPLCV140:0207/tblSAPLCV140SUB_DOC/ctxtDRAW-DOKVR[3,0]").text = ""
#     # session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subDOC_ALV:SAPLCV140:0207/tblSAPLCV140SUB_DOC/ctxtDRAW-DOKNR[1,0]").setFocus()
#     # session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subDOC_ALV:SAPLCV140:0207/tblSAPLCV140SUB_DOC/ctxtDRAW-DOKNR[1,0]").caretPosition = 0
#     # session.findById("wnd[0]").sendVKey(0)
#     # session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\TAB17/ssubSUB_GROUP_10:SAPLIQS0:7220/subSUBSCREEN_1:SAPLIQS0:7800/cntlDISPLAY_TEXT/shellcont/shell").setSelectionIndexes(171, 172)
#     # session.findById("wnd[0]/shellcont/shell").selectItem("0010", "Column01")
#     # session.findById("wnd[0]/shellcont/shell").ensureVisibleHorizontalItem("0010", "Column01")
#     # session.findById("wnd[0]/shellcont/shell").clickLink("0010", "Column01")
#     # session.findById("wnd[1]/usr/cntlCONTAINER/shellcont/shell[0]").expandNode("GWEN")
#     # session.findById("wnd[1]/usr/cntlCONTAINER/shellcont/shell[0]").expandNode("152TGM-ENGA")
#     # session.findById("wnd[1]/usr/cntlCONTAINER/shellcont/shell[0]").selectedNode = "000000001162"
#     # session.findById("wnd[1]/usr/cntlCONTAINER/shellcont/shell[0]").topNode = "AV2COM_WAU"
#     # session.findById("wnd[1]/usr/cntlCONTAINER/shellcont/shell[0]").doubleClickNode("000000001162")
#     # session.findById("wnd[1]/usr/cntlCONTAINER/shellcont/shell[0]").selectedNode = "000000001163"
#     # session.findById("wnd[1]/usr/cntlCONTAINER/shellcont/shell[0]").doubleClickNode("000000001163")
#     # session.findById("wnd[1]/usr/cntlCONTAINER/shellcont/shell[0]").selectedNode = "000000001164"
#     # session.findById("wnd[1]/usr/cntlCONTAINER/shellcont/shell[0]").doubleClickNode("000000001164")
#     # session.findById("wnd[1]/usr/cntlCONTAINER/shellcont/shell[0]").selectedNode = "000000001165"
#     # session.findById("wnd[1]/usr/cntlCONTAINER/shellcont/shell[0]").doubleClickNode("000000001165")
#     # session.findById("wnd[1]/usr/cntlCONTAINER/shellcont/shell[0]").selectedNode = "000000001166"
#     # session.findById("wnd[1]/usr/cntlCONTAINER/shellcont/shell[0]").doubleClickNode("000000001166")
#     # session.findById("wnd[1]/usr/cntlCONTAINER/shellcont/shell[0]").selectedNode = "000000001167"
#     # session.findById("wnd[1]/usr/cntlCONTAINER/shellcont/shell[0]").doubleClickNode("000000001167")
#     # session.findById("wnd[1]/usr/cntlCONTAINER/shellcont/shell[0]").selectedNode = "000000001168"
#     # session.findById("wnd[1]/usr/cntlCONTAINER/shellcont/shell[0]").doubleClickNode("000000001168")
#     # session.findById("wnd[1]/usr/cntlCONTAINER/shellcont/shell[0]").selectedNode = "000000001169"
#     # session.findById("wnd[1]/usr/cntlCONTAINER/shellcont/shell[0]").doubleClickNode("000000001169")
#     # session.findById("wnd[1]/usr/cntlCONTAINER2/shellcont/shell").modifyCell(0, "RESP", "THIAGOQM")
#     # session.findById("wnd[1]/usr/cntlCONTAINER2/shellcont/shell").modifyCell(1, "RESP", "THIAGOQM")
#     # session.findById("wnd[1]/usr/cntlCONTAINER2/shellcont/shell").modifyCell(2, "RESP", "THIAGOQM")
#     # session.findById("wnd[1]/usr/cntlCONTAINER2/shellcont/shell").modifyCell(3, "RESP", "THIAGOQM")
#     # session.findById("wnd[1]/usr/cntlCONTAINER2/shellcont/shell").modifyCell(4, "RESP", "THIAGOQM")
#     # session.findById("wnd[1]/usr/cntlCONTAINER2/shellcont/shell").modifyCell(5, "RESP", "THIAGOQM")
#     # session.findById("wnd[1]/usr/cntlCONTAINER2/shellcont/shell").modifyCell(6, "RESP", "THIAGOQM")
#     # session.findById("wnd[1]/usr/cntlCONTAINER2/shellcont/shell").modifyCell(7, "RESP", "THIAGOQM")
#     # session.findById("wnd[1]/usr/cntlCONTAINER2/shellcont/shell").setCurrentCell(-1, "")
#     # session.findById("wnd[1]/usr/cntlCONTAINER2/shellcont/shell").firstVisibleColumn = "SUB_GRUPO"
#     # session.findById("wnd[1]/usr/cntlCONTAINER2/shellcont/shell").selectAll()
#     # session.findById("wnd[1]/tbar[0]/btn[44]").press()
#     # session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\TAB17/ssubSUB_GROUP_10:SAPLIQS0:7220/subSUBSCREEN_1:SAPLIQS0:7800/cntlDISPLAY_TEXT/shellcont/shell").setSelectionIndexes(0, 0)
#     # session.findById("wnd[0]/tbar[1]/btn[14]").press()
#     # session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\TAB17/ssubSUB_GROUP_10:SAPLIQS0:7220/subSUBSCREEN_1:SAPLIQS0:7800/cntlDISPLAY_TEXT/shellcont/shell").setSelectionIndexes(0, 0)
#     # session.findById("wnd[0]/usr/subSCREEN_1:SAPLIQS0:1090/txtVIQMEL-QMNUM").setFocus()
#     # session.findById("wnd[0]/usr/subSCREEN_1:SAPLIQS0:1090/txtVIQMEL-QMNUM").caretPosition = 9
#     # session.findById("wnd[0]/tbar[0]/btn[11]").press()
#     # session.findById("wnd[0]/mbar/menu[0]/menu[1]").select()
#     # session.findById("wnd[0]").sendVKey(0)
#     # session.findById("wnd[0]/tbar[0]/btn[3]").press()
#     # session.findById("wnd[0]/usr/ctxtRIWO00-QMNUM").text = "422748794"
#     # session.findById("wnd[0]").sendVKey(0)
#     # session.findById("wnd[0]/tbar[0]/btn[3]").press()
#     # session.findById("wnd[0]/tbar[0]/btn[3]").press()
#     # session.findById("wnd[0]/tbar[0]/okcd").text = "IQS12"
#     # session.findById("wnd[0]").sendVKey(0)
#     # session.findById("wnd[0]/usr/ctxtRIWOSM-MANUM").setFocus()
#     # session.findById("wnd[0]/usr/ctxtRIWOSM-MANUM").caretPosition = 0
#     # session.findById("wnd[0]").sendVKey(4)
#     # session.findById("wnd[1]").close()
#     # session.findById("wnd[0]/tbar[0]/btn[3]").press()
#     # session.findById("wnd[0]/tbar[0]/btn[15]").press()
#     # session.findById("wnd[0]/tbar[0]/okcd").text = "IQS22"
#     # session.findById("wnd[0]").sendVKey(0)
#     # session.findById("wnd[0]/shellcont/shell").selectItem("0010", "Column01")
#     # session.findById("wnd[0]/shellcont/shell").ensureVisibleHorizontalItem("0010", "Column01")
#     # session.findById("wnd[0]/shellcont/shell").clickLink("0010", "Column01")
#     # session.findById("wnd[1]/usr/cntlCONTAINER2/shellcont/shell").firstVisibleColumn = "SUB_GRUPO"
#     # session.findById("wnd[1]").close()
#     # session.findById("wnd[0]/tbar[0]/btn[3]").press()
#     # session.findById("wnd[0]/tbar[0]/btn[3]").press()
#     # # session.findById("wnd[0]/tbar[0]/okcd").text = "IW32"
#     # # session.findById("wnd[0]").sendVKey(0)
#     # # session.findById("wnd[0]/usr/ctxtCAUFVD-AUFNR").text = ""
#     # # session.findById("wnd[0]/usr/ctxtCAUFVD-AUFNR").caretPosition = 1
#     # # session.findById("wnd[0]/tbar[0]/btn[3]").press()
#     # # session.findById("wnd[0]/tbar[0]/okcd").text = "IW52"
#     # # session.findById("wnd[0]").sendVKey(0)
#     # # session.findById("wnd[0]/usr/ctxtRIWO00-QMNUM").text = "422748794"
#     # # session.findById("wnd[0]/usr/ctxtRIWO00-QMNUM").caretPosition = 9
#     # # session.findById("wnd[0]").sendVKey(0)
#     # # session.findById("wnd[0]/tbar[0]/btn[15]").press()
#     # # session.findById("wnd[0]/tbar[0]/okcd").text = "IW22"
#     # # session.findById("wnd[0]").sendVKey(0)
#     # # session.findById("wnd[0]/usr/ctxtRIWO00-QMNUM").text = "422748794"
#     # # session.findById("wnd[0]/usr/ctxtRIWO00-QMNUM").caretPosition = 9
#     # # session.findById("wnd[0]").sendVKey(0)
#     # # session.findById("wnd[0]/tbar[0]/btn[3]").press()
#     # # session.findById("wnd[0]/tbar[0]/okcd").text = "CLM2"
#     # # session.findById("wnd[0]").sendVKey(0)
#     # # session.findById("wnd[0]/usr/ctxtRIWO00-QMNUM").text = "422748794"
#     # # session.findById("wnd[0]/usr/ctxtRIWO00-QMNUM").caretPosition = 9
#     # # session.findById("wnd[0]").sendVKey(0)
#     # # session.findById("wnd[0]/tbar[0]/btn[3]").press()
#     # # session.findById("wnd[0]/tbar[0]/btn[3]").press()
#     # session.findById("wnd[0]/tbar[0]/okcd").text = "IQS12"
#     # session.findById("wnd[0]").sendVKey(0)
#     # session.findById("wnd[0]/usr/ctxtRIWOSM-MANUM").text = "2"
#     # session.findById("wnd[0]/usr/ctxtRIWOSM-MANUM").setFocus()
#     # session.findById("wnd[0]/usr/ctxtRIWOSM-MANUM").caretPosition = 1
#     # session.findById("wnd[0]").sendVKey(0)
#     # session.findById("wnd[0]/tbar[1]/btn[45]").press()
#     # session.findById("wnd[0]/usr/cntlDISPLAY_LTXTMASSN/shellcont/shell").setSelectionIndexes(0, 0)
#     # session.findById("wnd[0]/tbar[0]/btn[11]").press()
#     # session.findById("wnd[0]/usr/ctxtRIWOSM-MANUM").text = "3"
#     # session.findById("wnd[0]/usr/ctxtRIWOSM-MANUM").setFocus()
#     # session.findById("wnd[0]/usr/ctxtRIWOSM-MANUM").caretPosition = 1
#     # session.findById("wnd[0]").sendVKey(0)
#     # session.findById("wnd[0]").sendVKey(0)
#     # session.findById("wnd[0]/usr/cntlDISPLAY_LTXTMASSN/shellcont/shell").setSelectionIndexes(0, 0)
#     # session.findById("wnd[0]/tbar[1]/btn[45]").press()
#     # session.findById("wnd[0]/usr/cntlDISPLAY_LTXTMASSN/shellcont/shell").setSelectionIndexes(0, 0)
#     # session.findById("wnd[0]/tbar[0]/btn[11]").press()
#     # session.findById("wnd[0]/usr/ctxtRIWOSM-MANUM").text = "4"
#     # session.findById("wnd[0]/usr/ctxtRIWOSM-MANUM").setFocus()
#     # session.findById("wnd[0]/usr/ctxtRIWOSM-MANUM").caretPosition = 1
#     # session.findById("wnd[0]").sendVKey(0)
#     # session.findById("wnd[0]/tbar[1]/btn[45]").press()
#     # session.findById("wnd[0]/usr/cntlDISPLAY_LTXTMASSN/shellcont/shell").setSelectionIndexes(0, 0)
#     # session.findById("wnd[0]/tbar[0]/btn[11]").press()
#     # session.findById("wnd[0]/usr/ctxtRIWOSM-MANUM").text = "5"
#     # session.findById("wnd[0]/usr/ctxtRIWOSM-MANUM").setFocus()
#     # session.findById("wnd[0]/usr/ctxtRIWOSM-MANUM").caretPosition = 1
#     # session.findById("wnd[0]").sendVKey(0)
#     # session.findById("wnd[0]/tbar[1]/btn[45]").press()
#     # session.findById("wnd[0]/usr/cntlDISPLAY_LTXTMASSN/shellcont/shell").setSelectionIndexes(0, 0)
#     # session.findById("wnd[0]/tbar[0]/btn[11]").press()
#     # session.findById("wnd[0]/usr/ctxtRIWOSM-MANUM").text = "6"
#     # session.findById("wnd[0]/usr/ctxtRIWOSM-MANUM").setFocus()
#     # session.findById("wnd[0]/usr/ctxtRIWOSM-MANUM").caretPosition = 1
#     # session.findById("wnd[0]").sendVKey(0)
#     # session.findById("wnd[0]/tbar[1]/btn[45]").press()
#     # session.findById("wnd[0]/usr/cntlDISPLAY_LTXTMASSN/shellcont/shell").setSelectionIndexes(0, 0)
#     # session.findById("wnd[0]/tbar[0]/btn[11]").press()
#     # session.findById("wnd[0]/usr/ctxtRIWOSM-MANUM").text = "7"
#     # session.findById("wnd[0]/usr/ctxtRIWOSM-MANUM").setFocus()
#     # session.findById("wnd[0]/usr/ctxtRIWOSM-MANUM").caretPosition = 1
#     # session.findById("wnd[0]").sendVKey(0)
#     # session.findById("wnd[0]/tbar[1]/btn[45]").press()
#     # session.findById("wnd[0]/usr/cntlDISPLAY_LTXTMASSN/shellcont/shell").setSelectionIndexes(0, 0)
#     # session.findById("wnd[0]/tbar[0]/btn[11]").press()
#     # session.findById("wnd[0]/usr/ctxtRIWOSM-MANUM").text = "8"
#     # session.findById("wnd[0]/usr/ctxtRIWOSM-MANUM").setFocus()
#     # session.findById("wnd[0]/usr/ctxtRIWOSM-MANUM").caretPosition = 1
#     # session.findById("wnd[0]").sendVKey(0)
#     # session.findById("wnd[0]/tbar[1]/btn[45]").press()
#     # session.findById("wnd[0]/usr/cntlDISPLAY_LTXTMASSN/shellcont/shell").setSelectionIndexes(0, 0)
#     # session.findById("wnd[0]/tbar[0]/btn[11]").press()
#     # session.findById("wnd[0]/usr/ctxtRIWOSM-MANUM").text = "9"
#     # session.findById("wnd[0]/usr/ctxtRIWOSM-MANUM").setFocus()
#     # session.findById("wnd[0]/usr/ctxtRIWOSM-MANUM").caretPosition = 1
#     # session.findById("wnd[0]").sendVKey(0)


# # if __name__ == "__main__":
# #     x = createZZ()
# #     print(x)
   







   

 
 