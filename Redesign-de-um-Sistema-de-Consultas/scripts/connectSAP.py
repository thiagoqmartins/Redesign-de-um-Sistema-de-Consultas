import win32com.client
import subprocess
import time
import sys
import json
import os
import sqlite3
from regex import R, U
from sympy import li


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
    db_path = os.path.normpath(os.path.join(project_root, 'PROJETO1','BD', 'banco_dados.db'))
    # opcional: garantir que a pasta exista
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return db_path

def conectar():
    try:
        SapGuiAuto = None
        session = None

        try:
            SapGuiAuto = win32com.client.GetObject("SAPGUI")
            print("SAP GUI já está aberto.")
            
            if SapGuiAuto.GetScriptingEngine.Children.Count > 0:
                session = SapGuiAuto.GetScriptingEngine.Children(0).Children(0)
                print("Sessão ativa encontrada.")
                mandante = session.Info.Client
                language = session.Info.Language              
                numero_sessoes = session.Parent.Children.Count
                sessoes = {}

                for i in range(numero_sessoes):
                    chave = f"sessao_{i+1}"                    
                    sessoes[chave] = session.Parent.Children(i)                      
                                        

                if mandante == "100" and language == "PT": 
                    return sessoes['sessao_1']                                   
                       
        except:           
            print("SAP GUI não está aberto. Iniciando...")
            subprocess.Popen(r'C:\Program Files (x86)\SAP\FrontEnd\SAPgui\saplgpad.exe')
            time.sleep(5)  # Pode ser refinado com loop de verificação

        # Aguarda o SAP GUI iniciar completamente
        SapGuiAuto = win32com.client.GetObject("SAPGUI")
        application = SapGuiAuto.GetScriptingEngine



        # Abre conexão
        connection = application.OpenConnection("EP0 - ECC Produção", False)
        time.sleep(2)

        session = connection.Children(0)

        usuario, senha = credenciais()  
        # Login
        session.findById("wnd[0]/usr/txtRSYST-MANDT").text = "100"
        session.findById("wnd[0]/usr/txtRSYST-BNAME").text = usuario
        session.findById("wnd[0]/usr/pwdRSYST-BCODE").text = senha
        session.findById("wnd[0]/usr/txtRSYST-LANGU").text = "PT"
        session.findById("wnd[0]/tbar[0]/btn[0]").press()

        # Aguarda carregamento
        time.sleep(3)

        # Restaura após login
        session.findById("wnd[0]").restore()

        print("Login SAP realizado com sucesso.")
        return session
    
    except Exception as e:
        print(f"Erro ao conectar ao SAP: {str(e)}")
        return None
    
def credenciais():    

    DB_PATH = get_db_path()
    conn = sqlite3.connect(DB_PATH)
 

    try:
        cur = conn.cursor()
        cur.execute("SELECT user, pass FROM credenciais_sap LIMIT 1;")
        row = cur.fetchone()
        if not row:
            raise RuntimeError("Nenhuma credencial encontrada em credenciais_sap.")
        usuario, senha = row
        print(usuario)
        return usuario, senha
    finally:
        conn.close()




   
    
   




    
    
