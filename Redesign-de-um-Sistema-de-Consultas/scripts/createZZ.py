# createZZ.py
import os
import re
import sys
import json
import sqlite3
import time
import ast

from ctypes.wintypes import PINT
from tracemalloc import stop
from numpy import empty
from qtd_atividade import ver_qtd
from huggingface_hub import ChatCompletionOutputLogprobs
from regex import R
from sympy import li
from typing import List, Dict, Tuple, Any


# ======= Força UTF-8 no stdout/stderr (evita UnicodeEncodeError em Windows) =======
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUTF8"] = "1"
if hasattr(sys.stdout, "reconfigure"): #Concluido
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# ======= Import do conector SAP (mantém sua estrutura de pastas) =======
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.connectSAP import conectar  # noqa: E402


# ======= Helpers de saída padronizada =======
def ok(payload=None): #Concluido
    """Imprime JSON de sucesso e sai com código 0."""
    print(json.dumps({"ok": True, "resultado": payload}, ensure_ascii=False))
    sys.exit(0)

def fail(msg, extra=None): #Concluido
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

# ======= Lógica principal =======
def createZZ(): #Em Andamento    

    DB_PATH = get_db_path()   
    
    conn = sqlite3.connect(DB_PATH)
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
# 
# #TAG       → Claim Modelo
#NT        → 7 (Cálculo Turbina > Cálculo Redutor > Segurança e Controle > Acessórios > Estudos Redutores > Estudos Turbinas > Documentação) 422865324
#NR        → 4 (Cálculo Redutor > Segurança e Controle > Estudos Redutor > Documentação) 422866933
#ST        → 5 (Cálculo Turbina > Cálculo Redutor > Segurança e Controle > Estudos > Partes e Peças) 422866934
#SR        → 4 (Cálculo Redutor > Segurança e Controle > Estudos > Partes e Peças) 422867362
#GT        → 6 (Cálculo Turbina > Cálculo Redutor > Segurança e Controle > Acessórios > Estudos > Documentação) 422867363
#GR        → 4 (Cálculo Redutor > Segurança e Controle > Estudos > Documentação) 422867365
#GST       → 5 (Cálculo Turbina > Cálculo Redutor > Segurança e Controle > Estudos > Partes e Peças) 422867366    
#GSR       → 4 (Cálculo Redutor > Segurança e Controle > Estudos > Partes e Peças) 422867367
#AT-T      → 5 (Cálculo Turbina > Cálculo Redutor > Segurança e Controle > Estudos > Partes e Peças) 422867368
#AT-R      → 4 (Cálculo Redutor > Segurança e Controle > Estudos > Partes e Peças) 422867369          
    
    session = conectar()
   
    for linha in linhas:  
        claim = linha[1]       
        claimModelo, responsaveis, qtd, erro = quantidadeMedidas(linha[18])  
        qtd = int(qtd)       
        conteudo, descricao, tipoDocumento, numDocumento, dop, vs = buscar_informacoes(session, claim) 
        if not erro:     
            if not session:
                fail("Não foi possível conectar ao SAP (session=None).")       
        
            session.findById("wnd[0]/tbar[0]/okcd").text = "/nclm1"
            session.findById("wnd[0]").sendVKey(0)
            session.findById("wnd[0]/usr/cmbRIWO00-QMART").key = "ZZ"
            session.findById("wnd[0]/usr/ctxtRIWO00-QWRNUM").text = claimModelo
            session.findById("wnd[0]").sendVKey(0)  
            session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB01/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_1:SAPLIQS0:7715/txtRIWO00-HEADKTXT").text = descricao  # class_bu
            session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB01/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPMCLAIM:7800/ctxtCLAIM-URGRP").text = "01"
            session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB01/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPMCLAIM:7800/ctxtCLAIM-URCOD").text = "0001"
            session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB01/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_1:SAPLIQS0:7715/cntlTEXT/shellcont/shell").text = "Claim (ZO) Origem: " + claim +  "\n"  + "\n" + conteudo
            session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB01/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPMCLAIM:7800/cmbVIQMEL-PRIOK").key = "1"
            session.findById("wnd[0]").sendVKey(0)       
            x = 0
            #documentos
            for item in tipoDocumento:
                if item != "":            
                    session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB02").select()
                    session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subBUTTON:SAPLCV140:0203/radGF_ALLE").select()
                    session.findById(f'wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subDOC_ALV:SAPLCV140:0207/tblSAPLCV140SUB_DOC/ctxtDRAW-DOKAR[0,{x}]').text = tipoDocumento[x]
                    session.findById(f'wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subDOC_ALV:SAPLCV140:0207/tblSAPLCV140SUB_DOC/ctxtDRAW-DOKNR[1,{x}]').text = numDocumento[x]
                    session.findById(f'wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subDOC_ALV:SAPLCV140:0207/tblSAPLCV140SUB_DOC/ctxtDRAW-DOKTL[2,{x}]').text = dop[x]
                    session.findById(f'wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subDOC_ALV:SAPLCV140:0207/tblSAPLCV140SUB_DOC/ctxtDRAW-DOKVR[3,{x}]').text = vs[x]
                    session.findById("wnd[0]").sendVKey(0)
                    x += 1        

            session.findById("wnd[0]/shellcont/shell").selectItem("0010", "Column01")
            session.findById("wnd[0]/shellcont/shell").ensureVisibleHorizontalItem("0010", "Column01")
            session.findById("wnd[0]/shellcont/shell").clickLink("0010", "Column01")
            grid = session.findById("wnd[1]/usr/cntlCONTAINER2/shellcont/shell")


            y = 0
            try:
                for nome in responsaveis:         
                    if isinstance(nome, list):       
                        nomeSAP = str(nome[0])
                    elif isinstance(nome, str) and nome.startswith("["):               
                        try:
                            nomeSAP = ast.literal_eval(nome)[0]
                        except:                   
                            nomeSAP = nome.strip("[]'\" ")
                    else:              
                        nomeSAP = str(nome)
                    # nomeSAP = "THIAGOQM" #EXCLUIR LINHA, APENAS PARA TESTES.  
                    grid.modifyCell(y, "RESP", nomeSAP)
                    y += 1
            except:
                return("Erro")        

            session.findById("wnd[1]/usr/cntlCONTAINER2/shellcont/shell").selectAll()
            session.findById("wnd[1]/tbar[0]/btn[44]").press()

            nClaimZZ = session.findById("wnd[0]/usr/subSCREEN_1:SAPLIQS0:1090/txtVIQMEL-QMNUM").text
            
            session.findById("wnd[0]/tbar[0]/btn[11]").press() 
            
            liberarMedidas(nClaimZZ, session, qtd)  
            atualizaBDconsulta(nClaimZZ, claim, y)   
            ver_qtd()
        else:
            msgErro = "" #Definir rotina para erro de atribuir usuario
        
        

    conn.close() 
    return "Concluído"

def liberarMedidas(nClaim, session, qtd): #Concluido

    session.findById("wnd[0]/tbar[0]/okcd").text = "/nclm2"
    session.findById("wnd[0]").sendVKey(0)
    session.findById("wnd[0]/usr/ctxtRIWO00-QMNUM").text = nClaim
    session.findById("wnd[0]").sendVKey(0)    
    session.findById("wnd[0]/tbar[1]/btn[14]").press()
    session.findById("wnd[0]/tbar[0]/btn[11]").press()

    qtd = qtd + 1 
    for x in range (2, qtd):
     
        session.findById("wnd[0]/tbar[0]/okcd").text = "/niqs12"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/ctxtRIWOSM-MANUM").text = x  
        session.findById("wnd[0]/usr/ctxtRIWOSM-MANUM").setFocus()
        session.findById("wnd[0]/usr/ctxtRIWOSM-MANUM").caretPosition = 1
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/tbar[1]/btn[45]").press()
        session.findById("wnd[0]/tbar[0]/btn[11]").press()


    return

def atualizaBDconsulta(nClaimZZ, claim, nMedidas): #Concluído

    DB_PATH = get_db_path()

    conn = sqlite3.connect(DB_PATH)  # Ajuste o caminho/conexão
    cursor = conn.cursor()

    query = """
    UPDATE consultas_iqs9
    SET num_claimzz = ?,
        status_claimZZ = ?,
        qtdMedida = ?,
        qtdFinalizada
    WHERE numero_nota = ?
    """
    cursor.execute(query, (nClaimZZ, "Em processo", nMedidas, 0, claim))
    conn.commit()

    return

def normaliza_resp(resp):
    """Extrai apenas o texto limpo do responsável"""
    if resp is None:
        return ""
    
    if isinstance(resp, list):
        if len(resp) == 0:
            return ""
        if len(resp) == 1:
            return str(resp[0]).strip()
        return str(resp)
    
    if isinstance(resp, str):
        resp_strip = resp.strip()
        if resp_strip.startswith('[') and resp_strip.endswith(']'):
            try:
                aval = ast.literal_eval(resp_strip)
                if isinstance(aval, list):
                    if len(aval) == 0:
                        return ""
                    if len(aval) == 1:
                        return str(aval[0]).strip()
                return str(aval)
            except Exception:
                # Fallback: remove colchetes e aspas manualmente
                return resp_strip.strip("[]'\" ").strip()
        return resp_strip
    
    return str(resp).strip()

def quantidadeMedidas(classBU: str) -> Tuple[str, List[str], str, str]: #Concluido
    """
    Retorna: (claim_modelo, responsaveis, qtd, erro)
    
    Parâmetros:
        classBU: Código da classe de negócio (1-10)
    
    Retorno:
        claim_modelo: Número do modelo de claim
        responsaveis: Lista de responsáveis (strings limpas)
        qtd: Quantidade de medidas (string)
        erro: "erro" se algum responsável vier vazio, "" caso contrário
    """
    
    # Configuração centralizada por classBU
    CONFIG = {
        "1": {  # NT → 7 medidas
            "claim_modelo": "422865324",
            "qtd": "7",
            "paths": [
                ["Turbinas", "Novos", "Calculos"],
                ["Redutores", "Novos", "Calculos"],
                ["Turbinas", "Novos", "Seg_Controle"],
                ["Turbinas", "Novos", "Acessorios"],
                ["Redutores", "Novos", "Estudos"],
                ["Turbinas", "Novos", "Estudos"],
                ["Turbinas", "Novos", "Documentos"],
            ]
        },
        "2": {  # NR → 4 medidas
            "claim_modelo": "422866933",
            "qtd": "4",
            "paths": [
                ["Redutores", "Novos", "Calculos"],
                ["Redutores", "Novos", "Seg_Controle"],
                ["Redutores", "Novos", "Estudos"],
                ["Redutores", "Novos", "Documentos"],
            ]
        },
        "3": {  # ST → 5 medidas
            "claim_modelo": "422866934",
            "qtd": "5",
            "paths": [
                ["Turbinas", "Serviços", "Calculos"],
                ["Redutores", "Serviços", "Calculos"],
                ["Turbinas", "Serviços", "Seg_Controle"],
                ["Turbinas", "Serviços", "Estudos"],
                ["Turbinas", "Serviços", "Acessorios"],
            ]
        },
        "4": {  # SR → 4 medidas
            "claim_modelo": "422867362",
            "qtd": "4",
            "paths": [
                ["Redutores", "Serviços", "Calculos"],
                ["Redutores", "Serviços", "Seg_Controle"],
                ["Redutores", "Serviços", "Estudos"],
                ["Redutores", "Serviços", "Documentos"],
            ]
        },
        "5": {  # GT → 6 medidas
            "claim_modelo": "422867363",
            "qtd": "6",
            "paths": [
                ["Turbinas", "Novos", "Calculos"],
                ["Redutores", "Novos", "Calculos"],
                ["Turbinas", "Novos", "Seg_Controle"],
                ["Turbinas", "Novos", "Acessorios"],
                ["Turbinas", "Novos", "Estudos"],
                ["Turbinas", "Novos", "Documentos"],
            ]
        },
        "6": {  # GR → 4 medidas
            "claim_modelo": "422867365",
            "qtd": "4",
            "paths": [
                ["Redutores", "Novos", "Calculos"],
                ["Redutores", "Novos", "Seg_Controle"],
                ["Redutores", "Novos", "Estudos"],
                ["Redutores", "Novos", "Documentos"],
            ]
        },
        "7": {  # GST → 5 medidas
            "claim_modelo": "422867366",
            "qtd": "5",
            "paths": [
                ["Turbinas", "Serviços", "Calculos"],
                ["Redutores", "Serviços", "Calculos"],
                ["Turbinas", "Serviços", "Seg_Controle"],
                ["Turbinas", "Serviços", "Estudos"],
                ["Turbinas", "Serviços", "Acessorios"],
            ]
        },
        "8": {  # GSR → 4 medidas
            "claim_modelo": "422867367",
            "qtd": "4",
            "paths": [
                ["Redutores", "Serviços", "Calculos"],
                ["Redutores", "Serviços", "Seg_Controle"],
                ["Redutores", "Serviços", "Estudos"],
                ["Redutores", "Serviços", "Documentos"],
            ]
        },
        "9": {  # AT-T → 5 medidas
            "claim_modelo": "422867368",
            "qtd": "5",
            "paths": [
                ["Turbinas", "Serviços", "Calculos"],
                ["Redutores", "Serviços", "Calculos"],
                ["Turbinas", "Serviços", "Seg_Controle"],
                ["Turbinas", "Serviços", "Estudos"],
                ["Turbinas", "Serviços", "Acessorios"],
            ]
        },
        "10": {  # AT-R → 4 medidas
            "claim_modelo": "422867369",
            "qtd": "4",
            "paths": [
                ["Redutores", "Serviços", "Calculos"],
                ["Redutores", "Serviços", "Seg_Controle"],
                ["Redutores", "Serviços", "Estudos"],
                ["Redutores", "Serviços", "Documentos"],
            ]
        },
    }
    
    # Inicializa variáveis de retorno
    responsaveis: List[str] = []
    erro = ""
    
    # Valida classBU
    cfg = CONFIG.get(classBU)
    if not cfg:
        return ("", [], "", f"classBU inválido: {classBU}")
    
    claim_modelo = cfg["claim_modelo"]
    qtd = cfg["qtd"]
    
    # Processa cada responsável
    for path in cfg["paths"]:
        resp = definir_responsavel(path)
        resp_normalizado = normaliza_resp(resp)
        
        # Verifica se veio vazio
        if not resp_normalizado or resp_normalizado.strip() == "":
            erro = "erro"
        
        responsaveis.append(resp_normalizado)
    
    return (claim_modelo, responsaveis, qtd, erro)

def definir_responsavel(campos: List[str]) -> List[Dict[str, any]]: #Concluido
    DB_PATH = get_db_path()

    where = " AND ".join([f"COALESCE({c},0)=1" for c in campos])
    query = f"""
        SELECT nome_resp, COALESCE(qtd_atividade,0) AS qtd_atividade
        FROM responsaveis
        WHERE COALESCE(resp_ativo,0)=1
        AND {where}
        AND (
                inicio_aus IS NULL
            OR fim_aus IS NULL
            OR DATE('now') < DATE(inicio_aus)
            OR DATE('now') > DATE(fim_aus)
        )
        ORDER BY COALESCE(qtd_atividade,0) ASC, nome_resp COLLATE NOCASE ASC
        LIMIT 1;
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.execute(query)
        rows = cur.fetchall()           
        return [(row[0]) for row in rows]
    finally:
        conn.close()

def criarMedidas(session, medida, userSap, nMedida): #Avaliar, pode ser eliminada
    
    # Supõe: session = ...  (objeto SAP GUI ativo via win32com.client)
    TREE_ID = r"wnd[1]/usr/cntlCONTAINER/shellcont/shell[0]"
    tree = session.findById(TREE_ID)

    medida = medida.strip()  # ajuste conforme sua variável de comparação
    encontrado = False

    for i in range(100, 2001):  # inclui 2000
        campo = f"{i:012d}"     # equivalente ao seu padding com 9/8 zeros

        try:
            # Tente pegar o texto do nó diretamente pela chave (mais rápido)
            nomee = tree.GetNodeTextByKey(campo).strip()
        except Exception:
            # Se a chave não existir, só pula para o próximo i
            continue

        if nomee == medida:
            # Seleciona e rola o nó (compatível com variações de API)
            try:
                tree.SelectedNode = campo     # algumas versões aceitam propriedade
            except Exception:
                try:
                    tree.SelectNode(campo)    # outras expõem como método
                except Exception:
                    pass

            try:
                tree.TopNode = campo          # propriedade para levar o nó ao topo
            except Exception:
                try:
                    tree.topNode = campo      # em alguns ambientes o case varia
                except Exception:
                    pass

            encontrado = True
            break

    # Se precisar continuar o fluxo do rótulo PROXIMO:
    if encontrado:

        session.findById("wnd[1]/usr/cntlCONTAINER/shellcont/shell[0]").DoubleClickNode(campo)
        # session.findById("wnd[2]/usr/btnBUTTON_2").Press
        session.findById("wnd[1]/usr/cntlCONTAINER2/shellcont/shell").modifyCell(nMedida, "RESP", userSap)

        pass
    else:
        # ... tratamento quando não encontrar ...
        pass

def buscar_informacoes(session, numero_nota): #Parcialmente Concluido
    tipoDocumento = []   
    numDocumento = []
    dop = []
    vs = []
    # descDocumento = []
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
    nDocAnt = ""
    i = 1
    while True:
        try:            
            tpDoc = session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subDOC_ALV:SAPLCV140:0207/tblSAPLCV140SUB_DOC/ctxtDRAW-DOKAR[0,0]").text
            nDoc = session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subDOC_ALV:SAPLCV140:0207/tblSAPLCV140SUB_DOC/ctxtDRAW-DOKNR[1,0]").text
            nDoP = session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subDOC_ALV:SAPLCV140:0207/tblSAPLCV140SUB_DOC/ctxtDRAW-DOKTL[2,0]").text
            nVs = session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subDOC_ALV:SAPLCV140:0207/tblSAPLCV140SUB_DOC/ctxtDRAW-DOKVR[3,0]").text
          
            if nDoc == nDocAnt:               
                break
            elif tpDoc == "":                 
                break

            tipoDocumento.append(tpDoc)
            numDocumento.append(nDoc)
            dop.append(nDoP)        
            vs.append(nVs)
            # descDocumento.append(valDesc)   
            session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subDOC_ALV:SAPLCV140:0207/tblSAPLCV140SUB_DOC").verticalScrollbar.position = i
            i += 1
            nDocAnt = nDoc
            print(i)

        except:
            break
    for nd in numDocumento:
        print (nd)

   
    return conteudo_claim, descricao, tipoDocumento, numDocumento, dop, vs

if __name__ == "__main__": #Função Principal, não excluir
    try:
        resultado = createZZ()
        ok()
    except Exception as e:
        # Devolve erro como JSON e exit code 1 (o Node responderá 500)
        fail("Falha ao criar ZZ")
