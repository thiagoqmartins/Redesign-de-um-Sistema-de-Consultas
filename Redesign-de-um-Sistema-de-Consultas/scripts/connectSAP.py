import win32com.client
import subprocess
import time
# import getpass

def conectar():
    try:
        SapGuiAuto = None
        session = None

        try:
            SapGuiAuto = win32com.client.GetObject("SAPGUI")
            print("✅ SAP GUI já está aberto.")

            if SapGuiAuto.GetScriptingEngine.Children.Count > 0:
                session = SapGuiAuto.GetScriptingEngine.Children(0).Children(0)
                print("✅ Sessão ativa encontrada.")
                mandante = session.Info.Client
                language = session.Info.Language              
                numero_sessoes = session.Parent.Children.Count
                sessoes = {}

                # if numero_sessoes < 5:
                #     print(numero_sessoes)
                #     print(dir(session.Parent.Children))

                for i in range(numero_sessoes):
                    chave = f"sessao_{i+1}"                    
                    sessoes[chave] = session.Parent.Children(i)                             

                if mandante == "100" and language == "PT":                   
                    return sessoes['sessao_1']                                   
                       
        except:
            print("🔄 SAP GUI não está aberto. Iniciando...")
            return("Erro")
        
            print("🔄 SAP GUI não está aberto. Iniciando...")
            subprocess.Popen(r'C:\Program Files (x86)\SAP\FrontEnd\SAPgui\saplgpad.exe')
            time.sleep(5)  # Pode ser refinado com loop de verificação

        # Aguarda o SAP GUI iniciar completamente
        SapGuiAuto = win32com.client.GetObject("SAPGUI")
        application = SapGuiAuto.GetScriptingEngine

        # Credenciais
        usuario = "thiagoqm"
        senha = "T@182213"

        # Abre conexão
        connection = application.OpenConnection("EP0 - ECC Produção", False)
        time.sleep(2)

        session = connection.Children(0)

        # Minimiza antes do login
        session.findById("wnd[0]").iconify()

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

        print("✅ Login SAP realizado com sucesso.")
        return session

    except Exception as e:
        print(f"❌ Erro ao conectar ao SAP: {str(e)}")
        return None


   
    
   




    
    
