import sys
import win32com.client
import importlib
import json
import subprocess
import time
import psutil#
import os
import re
import sqlite3
from regex import R, U
from sympy import li

# Força o uso de UTF-8 no Windows
sys.stdout.reconfigure(encoding='utf-8')

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
            print("SAP GUI já está aberto.", file=sys.stderr)
            if SapGuiAuto.GetScriptingEngine.Children.Count > 0:
                session = SapGuiAuto.GetScriptingEngine.Children(0).Children(0)
                print("Sessao ativa encontrada.", file=sys.stderr)
                return session
        except:
            print("SAP GUI nao esta aberto. Iniciando...", file=sys.stderr)
        subprocess.Popen(f'C:\\Program Files (x86)\\SAP\\FrontEnd\\SAPgui\\saplgpad.exe')
        print("Aguardando SAP GUI iniciar...", file=sys.stderr)

        for _ in range(10):  # tenta por até ~10 segundos
            try:
                SapGuiAuto = win32com.client.GetObject("SAPGUI")
                application = SapGuiAuto.GetScriptingEngine
                break  # sucesso
            except:
                time.sleep(1)
        else:
            raise Exception("❌ SAP GUI não respondeu após iniciar.")
       
        usuario, senha = credenciais()           

        connection = application.OpenConnection("EP0 - ECC Produção", False)
        time.sleep(2)
        session = connection.Children(0)
        try:
            session.findById("wnd[1]/tbar[0]/btn[0]").press
        except:

            session.findById("wnd[0]").iconify()
            session.findById("wnd[0]/usr/txtRSYST-MANDT").text = "100"
            session.findById("wnd[0]/usr/txtRSYST-BNAME").text = usuario
            session.findById("wnd[0]/usr/pwdRSYST-BCODE").text = senha
            session.findById("wnd[0]/usr/txtRSYST-LANGU").text = "PT"
            session.findById("wnd[0]/tbar[0]/btn[0]").press()

            time.sleep(3)
            session.findById("wnd[0]").restore()

            print("Login SAP realizado com sucesso.", file=sys.stderr)
            return session

    except Exception as e:
        print(f"Erro ao conectar ao SAP: {str(e)}", file=sys.stderr)
        return None
    return    

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

if __name__ == "__main__":
    session = None  # inicializa fora do try
    
    try:
        SapGuiAuto = win32com.client.GetObject("SAPGUI")        
        application = SapGuiAuto.GetScriptingEngine        
        connection = application.Children(0)
        
        if not connection or connection.Children.Count == 0:            
            raise Exception("Nenhuma sessão ativa encontrada.")
        
    except Exception as e:
        print("Tentando conectar...", file=sys.stderr)
        session = conectar()
        if session is None:
            print("Falha ao criar sessão SAP.", file=sys.stderr)
            sys.exit(1)
        connection = session.Parent
    else:
        session = connection.Children(0)

    # Agora session está garantida
    try:
        numero_sessoes = connection.Children.Count
        sessoes = {}

        for i in range(numero_sessoes):
            chave = f"sessao_{i+1}"
            sessoes[chave] = connection.Children(i)

        num_args = len(sys.argv)
        if num_args < 2:
            raise ValueError("Transação não foi informada!")

        transacao = sys.argv[1].lower()
        numero_sap = sys.argv[2].lower() if num_args > 2 else None        

        modulo = importlib.import_module(f"transacoes.trans_{transacao}")

        if numero_sap:
            resultado = modulo.executar(sessoes['sessao_1'], numero_sap)
        else:
            resultado = modulo.executar(sessoes['sessao_1'])

        print(json.dumps(resultado))

    except Exception as e:
        print(f"Erro durante a execução: {e}", file=sys.stderr)
        sys.exit(1)
    
    finally:
        # CRÍTICO: sempre fechar a sessão SAP
        if session:
            try:
                # Volta para a tela inicial e limpa o estado
                session.findById("wnd[0]/tbar[0]/okcd").text = "/n"
                session.findById("wnd[0]").sendVKey(0)
                
                print("✅ Sessão SAP encerrada com sucesso", file=sys.stderr)
            except Exception as close_error:
                print(f"⚠️ Erro ao fechar sessão SAP: {close_error}", file=sys.stderr)
                # Não faz sys.exit aqui para não mascarar o erro original