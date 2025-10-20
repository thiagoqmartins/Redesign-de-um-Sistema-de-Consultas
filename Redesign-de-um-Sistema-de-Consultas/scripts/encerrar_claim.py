import os
import sys
import json
import sqlite3
import time
from turtle import xcor
from networkx import k_edge_subgraphs
from regex import R
from sympy import li, true

os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUTF8"] = "1"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.connectSAP import conectar 

def ok(payload=None): #Concluido
    print(json.dumps({"ok": True, "resultado": payload}, ensure_ascii=False))
    sys.exit(0)

def fail(msg, extra=None):#Concluido
    out = {"ok": False, "erro": str(msg)}
    if extra is not None:        
        out["detalhe"] = str(extra)
    print(json.dumps(out, ensure_ascii=False))
    sys.exit(1)

def get_db_path(): #Concluido
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    db_path = os.path.normpath(os.path.join(project_root, 'BD', 'banco_dados.db')) 
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return db_path

def encerrarClaiZO():#Em Andamento

    DB_PATH = get_db_path()   
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor() 
    cursor.execute("""
    SELECT num_claimzz, qtdMedida, numero_nota
    FROM consultas_iqs9
    WHERE class_BU IS NOT NULL
        AND (
        num_claimzz IS NOT NULL
        OR (typeof(num_claimzz) = 'text' AND TRIM(num_claimzz) = '')
        )
        AND (
        qtdMedida =  qtdFinalizada)
    """)
    rows = cursor.fetchall() 
    conn.close()

    

    if rows:
        session = conectar()
    else:
        return
    
    for num_claim, qtdMedida, numero_nota in rows:        
        session.findById("wnd[0]/tbar[0]/okcd").text = "/nclm3"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/ctxtRIWO00-QMNUM").text = num_claim
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB11").select()

        responsavel = []
        dataResp = []

        for x in range (qtdMedida):           
            resp = session.findById(f'wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB11/ssubSUB_GROUP_10:SAPLIQS0:7120/tblSAPLIQS0MASSNAHMEN_VIEWER/txtVIQMSM-ERLNAM[15,{x}]').text        
            dataR = session.findById(f'wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB11/ssubSUB_GROUP_10:SAPLIQS0:7120/tblSAPLIQS0MASSNAHMEN_VIEWER/ctxtVIQMSM-ERLDAT[16,{x}]').text   
            responsavel.append(resp)
            dataResp.append(dataR)                   
        #    Selecionar e armazear os documentos
        session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB02").select()
        session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subBUTTON:SAPLCV140:0203/radGF_ALLE").select()

        tipoDocumento = []   
        numDocumento = []
        dop = []
        vs = []
        # descDocumento = []
        i = 0
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

                if tpDoc in ("ZFE", "ACD", "SWD"):
                    tipoDocumento.append(tpDoc)
                    numDocumento.append(nDoc)
                    dop.append(nDoP)        
                    vs.append(nVs)

                session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subDOC_ALV:SAPLCV140:0207/tblSAPLCV140SUB_DOC").verticalScrollbar.position = i
                i += 1
                nDocAnt = nDoc                
            except:
                break 
        incluirDocumentos(session, numero_nota, tipoDocumento, numDocumento, dop, vs)
        session.findById("wnd[0]/tbar[0]/btn[11]").press()     
        
        y = 1   
        textoResposta = []     
        while True:
            try:
                session.findById("wnd[0]").maximize                
                session.findById("wnd[0]/tbar[0]/okcd").text = "/niqs12"
                session.findById("wnd[0]").sendVKey(0)
                session.findById("wnd[0]/usr/ctxtRIWOSM-QMNUM").text = num_claim
                session.findById("wnd[0]/usr/ctxtRIWOSM-MANUM").text = y
                session.findById("wnd[0]/usr/ctxtRIWOSM-MANUM").setFocus
                session.findById("wnd[0]/usr/ctxtRIWOSM-MANUM").caretPosition = 1
                session.findById("wnd[0]").sendVKey(0)
                texto = session.findById("wnd[0]/usr/cntlDISPLAY_LTXTMASSN/shellcont/shell").text
                textoResposta.append(texto)                
                y = y + 1                
            except:
                break 

        resultado = ""
        for i, txt in enumerate(textoResposta):
            resultado += f"Medida concluída por: {responsavel[i]} em {dataResp[i]}\n"
            for nlin in txt.splitlines()[1:]:
                if nlin.strip():
                    resultado += nlin + "\n"
            resultado += "\n"        

        while True:
            try:
                session.findById("wnd[0]").maximize                
                session.findById("wnd[0]/tbar[0]/okcd").text = "/niqs12"
                session.findById("wnd[0]").sendVKey(0)
                session.findById("wnd[0]/usr/ctxtRIWOSM-QMNUM").text = numero_nota
                session.findById("wnd[0]/usr/ctxtRIWOSM-MANUM").text =1
                session.findById("wnd[0]/usr/ctxtRIWOSM-MANUM").setFocus
                session.findById("wnd[0]/usr/ctxtRIWOSM-MANUM").caretPosition = 1
                session.findById("wnd[0]").sendVKey(0)
                session.findById("wnd[0]/usr/cntlDISPLAY_LTXTMASSN/shellcont/shell").text = resultado  
                session.findById("wnd[0]/tbar[1]/btn[46]").press()
                session.findById("wnd[0]/tbar[0]/btn[11]").press()     
                return              
            except:
                break

        updateBD(numero_nota)           

    return

def documentosExistentes(session): #Concluido (Pode ser melhorado)
    a1 = []   
    b1 = []
    c1 = []
    d1 = []

    x = 0
    while True: 
        try:        
            a = session.findById(f'wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subDOC_ALV:SAPLCV140:0207/tblSAPLCV140SUB_DOC/ctxtDRAW-DOKAR[0,0]').text 
            b = session.findById(f'wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subDOC_ALV:SAPLCV140:0207/tblSAPLCV140SUB_DOC/ctxtDRAW-DOKNR[1,0]').text 
            c = session.findById(f'wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subDOC_ALV:SAPLCV140:0207/tblSAPLCV140SUB_DOC/ctxtDRAW-DOKTL[2,0]').text 
            d = session.findById(f'wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subDOC_ALV:SAPLCV140:0207/tblSAPLCV140SUB_DOC/ctxtDRAW-DOKVR[3,0]').text 
            if a == "":
                break
            a1.append(a)
            b1.append(b)
            c1.append(c)
            d1.append(d)
            x = x + 1
            session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subDOC_ALV:SAPLCV140:0207/tblSAPLCV140SUB_DOC").verticalScrollbar.position = x
        except:
            break
    return (a1, b1, c1, d1)

def incluirDocumentos(session, numero_nota, tipoDocumento, numDocumento, dop, vs):#Parcialmente Concluído (Necessário Validação)

    documentoAntigo = []
    documentoNovo = []
    session.findById("wnd[0]/tbar[0]/okcd").text = "/nclm2"
    session.findById("wnd[0]").sendVKey(0)
    session.findById("wnd[0]/usr/ctxtRIWO00-QMNUM").text = numero_nota
    session.findById("wnd[0]").sendVKey(0)     
    try:
        time.sleep(1)  
        session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB02").select()   
        session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subBUTTON:SAPLCV140:0203/radGF_ALLE").select()  
        a1, b1, c1, d1 = documentosExistentes(session)    
           
        for j in range(len(a1)):
            if a1[j] != "":
                documentoAntigo.append((f'{a1[j]}{b1[j]}{c1[j]}{d1[j]}')) 
          
        for i in range(len(tipoDocumento)):
            if tipoDocumento[i] != "":
                documentoNovo.append((f'{tipoDocumento[i]}{numDocumento[i]}{dop[i]}{vs[i]}'))
        k = 0
        
        while true:
            try:    
                session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subDOC_ALV:SAPLCV140:0207/tblSAPLCV140SUB_DOC").verticalScrollbar.position = k
                existeDoc = session.findById(f'wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subDOC_ALV:SAPLCV140:0207/tblSAPLCV140SUB_DOC/ctxtDRAW-DOKAR[0,{k}]').text  
                if not existeDoc.strip():
                    break                
                k += 1
            except Exception:    
                break

        for x in range(len(documentoNovo)):
            docExistente  =""  
            for z in range(len(documentoAntigo)):           
                if documentoAntigo[z] == documentoNovo[x]:   
                    docExistente = "SIM" 
                else:
                    continue    
            if docExistente == "":
                session.findById(f'wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subDOC_ALV:SAPLCV140:0207/tblSAPLCV140SUB_DOC/ctxtDRAW-DOKAR[0,0]').text = tipoDocumento[x]
                session.findById(f'wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subDOC_ALV:SAPLCV140:0207/tblSAPLCV140SUB_DOC/ctxtDRAW-DOKNR[1,0]').text = numDocumento[x]
                session.findById(f'wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subDOC_ALV:SAPLCV140:0207/tblSAPLCV140SUB_DOC/ctxtDRAW-DOKTL[2,0]').text = dop[x]
                session.findById(f'wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subDOC_ALV:SAPLCV140:0207/tblSAPLCV140SUB_DOC/ctxtDRAW-DOKVR[3,0]').text = vs[x]
                session.findById("wnd[0]").sendVKey(0)
                k = k + 1
                session.findById("wnd[0]/usr/tabsTAB_GROUP_10/tabp10\\TAB02/ssubSUB_GROUP_10:SAPLIQS0:7235/subCUSTOM_SCREEN:SAPLIQS0:7212/subSUBSCREEN_2:SAPLIQS0:7801/subDVS:SAPLCV140:0204/subDOC_ALV:SAPLCV140:0207/tblSAPLCV140SUB_DOC").verticalScrollbar.position = k
    except:
       return    
        
    return

def updateBD(num_claim):#Necessário validação

    DB_PATH = get_db_path()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE consultas_iqs9
        SET status = ?,
            status_claimZZ = ?
        WHERE numero_nota = ?
          AND class_BU IS NOT NULL
    """, ("Concluído", "Concluído", num_claim))
    
    conn.commit()
    conn.close()

    return

if __name__ == "__main__":
    try:
        resultado = encerrarClaiZO()
        ok(resultado)
    except Exception as e:
        # Devolve erro como JSON e exit code 1 (o Node responderá 500)
        fail("Falha ao executar", extra=repr(e))
