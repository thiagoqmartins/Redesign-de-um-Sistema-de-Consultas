
import sys
import win32com.client
import re
import json
import subprocess
import time

# Força o uso de UTF-8 no Windows
sys.stdout.reconfigure(encoding='utf-8')


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
        subprocess.Popen(r'C:\Program Files (x86)\SAP\FrontEnd\SAPgui\saplgpad.exe')
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


        usuario = "thiagoqm"
        senha = "T@182213"

        connection = application.OpenConnection("EP0 - ECC Produção", False)
        time.sleep(2)
        session = connection.Children(0)

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
    
def dados_claim(nclaim):
    session = sessao_sap()
    session.findById("wnd[0]").maximize()
    session.findById("wnd[0]/tbar[0]/okcd").text = "/nclm3"
    session.findById("wnd[0]").sendVKey(0)
    session.findById("wnd[0]/usr/ctxtRIWO00-QMNUM").text = nclaim
    session.findById("wnd[0]").sendVKey(0)
    session.findById(r"wnd[0]/usr/tabsTAB_GROUP_10/tabp10\TAB11").select()
    session.findById(r"wnd[0]/usr/tabsTAB_GROUP_10/tabp10\TAB17").select()
    TextoSintese = session.findById(r"wnd[0]/usr/tabsTAB_GROUP_10/tabp10\TAB17/ssubSUB_GROUP_10:SAPLIQS0:7220/subSUBSCREEN_1:SAPLIQS0:7800/cntlDISPLAY_TEXT/shellcont/shell").Text

    TextoSintese = limpar_texto_para_json(TextoSintese)
    # print (TextoSintese)
    return str(TextoSintese)

def limpar_texto_para_json(texto: str) -> str:
    # Remove caracteres de controle como \n, \r, \t (mas mantém espaço simples)
    texto = texto.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')

    # Remove tudo entre "Conteúdo" e ".."
    texto = re.sub(r'Conteúdo.*?\.\.', '', texto, flags=re.DOTALL)

    # Remove tudo entre "Status" e ".."
    texto = re.sub(r'Status.*?\.\.', '', texto, flags=re.DOTALL)

    # Remove espaços duplicados
    texto = re.sub(r'\s+', ' ', texto).strip()

    # Escapa aspas duplas
    texto = texto.replace('"', '\\"')

    return texto

def sessao_sap():
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

        return(sessoes['sessao_1'])

 

    except Exception as e:
        print(f"Erro durante a execução: {e}")
        sys.exit(1)


if __name__ == "__main__":
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

        dados_claim(sessoes['sessao_1'])

 

    except Exception as e:
        print(f"Erro durante a execução: {e}")
        sys.exit(1)


