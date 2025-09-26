# import sys
# import win32com.client
# import importlib
# import json
# from flask import Flask, request, jsonify
# import sqlite3

# import subprocess
# import time


# def conectar():

#     try:
#         SapGuiAuto = None
#         session = None

#         try:
#             SapGuiAuto = win32com.client.GetObject("SAPGUI")
#             print("✅ SAP GUI já está aberto.")

#             if SapGuiAuto.GetScriptingEngine.Children.Count > 0:
#                 session = SapGuiAuto.GetScriptingEngine.Children(0).Children(0)
#                 print("✅ Sessão ativa encontrada.")
#                 return session

#         except:
#             print("🔄 SAP GUI não está aberto. Iniciando...")
#             subprocess.Popen(r'C:\Program Files (x86)\SAP\FrontEnd\SAPgui\saplgpad.exe')
#             time.sleep(5)  # Pode ser refinado com loop de verificação

#         # Aguarda o SAP GUI iniciar completamente
#         SapGuiAuto = win32com.client.GetObject("SAPGUI")
#         application = SapGuiAuto.GetScriptingEngine

#         # Credenciais
#         usuario = "user"
#         senha = "senha"

#         # Abre conexão
#         connection = application.OpenConnection("EP0 - ECC Produção", False)
#         time.sleep(2)

#         session = connection.Children(0)

#         # Minimiza antes do login
#         session.findById("wnd[0]").iconify()

#         # Login
#         session.findById("wnd[0]/usr/txtRSYST-MANDT").text = "100"
#         session.findById("wnd[0]/usr/txtRSYST-BNAME").text = usuario
#         session.findById("wnd[0]/usr/pwdRSYST-BCODE").text = senha
#         session.findById("wnd[0]/usr/txtRSYST-LANGU").text = "PT"
#         session.findById("wnd[0]/tbar[0]/btn[0]").press()

#         # Aguarda carregamento
#         time.sleep(3)

#         # Restaura após login
#         session.findById("wnd[0]").restore()

#         print("✅ Login SAP realizado com sucesso.")
#         return session

#     except Exception as e:
#         print(f"❌ Erro ao conectar ao SAP: {str(e)}")
#         return None


# # Força o uso de UTF-8 no Windows
# sys.stdout.reconfigure(encoding='utf-8')

# try:
#     #----------
#     # Verifica se o SAP GUI está aberto e obtém a sessão ativa
#     # Importa o módulo win32com.client para interagir com o SAP GUI 
#     SapGuiAuto = win32com.client.GetObject("SAPGUI")
#     if not SapGuiAuto:        
#         raise Exception("SAP GUI não encontrado. Verifique se está aberto!")  
    
#     # Obtém o Scripting Engine do SAP GUI
#     # Isso permite interagir com o SAP GUI através de scripts
#     application = SapGuiAuto.GetScriptingEngine
#     if not application:   
#         raise Exception("Não foi possível obter o Scripting Engine.")
    
#     # Obtém a primeira conexão ativa do SAP GUI
#     # Isso é necessário para interagir com o SAP
#     connection = application.Children(0)     

#     if not connection:        
#         raise Exception("Nenhuma conexão encontrada. Você está logado no SAP?")
    
#     numero_sessoes = connection.Children.Count
#     sessoes = {}

#     for i in range(numero_sessoes):
#         chave = f"sessao_{i+1}"
#         sessoes[chave] = connection.Children(i)      

#         if not sessoes[chave]:
#             raise Exception("Nenhuma sessão ativa encontrada.")

#         # Verifica se o número de argumentos é menor que 2
#     nun_len = len(sys.argv)    

#     if nun_len < 2:
#         raise ValueError("❌ Transação não foi informada!")
#     # Se o número SAP for fornecido, ele deve ser o segundo argumento
#     transacao = sys.argv[1].lower()   
#     # Se o número SAP for fornecido, ele deve ser o terceiro argumento
#     numero_sap = sys.argv[2].lower() if nun_len > 2 else None   
    
#     # Verifica se a transação é válida
#     modulo = importlib.import_module(f"transacoes.trans_{transacao}")
#     modulo2 = importlib.import_module(f"transacoes.trans_clm3")    
#     modulo3 = importlib.import_module(f"scripts.createZZ")

#     # Verifica se o módulo foi carregado corretamente
#     if numero_sap:  
#         # Executa a transação com o número SAP fornecido
#         resultado = modulo.executar(sessoes['sessao_1'], numero_sap)        
#         # Imprime o resultado como JSON
#         print(json.dumps(resultado))
#     else:
#         # Executa a transação sem o número SAP
#         if sessoes.get('sessao_1'):
#             resultado = modulo.executar(sessoes['sessao_1'])  
#         # if sessoes.get('sessao_2'):
#         #     resultado_2 = modulo2.executar(sessoes['sessao_2'], "422617255")
#         # if sessoes.get('sessao_3'):
#         #     resultado_3 = modulo.executar(sessoes['sessao_3'])
#         # if sessoes.get('sessao_4'):
#         #     resultado_4 = modulo.executar(sessoes['sessao_4'])
#         # Imprime o resultado como JSON
#         print(json.dumps(resultado))
   

# except Exception as e:
#     print(f"❌ Erro ao conectar ao SAP: {e}")
#     sys.exit(1)  # Retornar código de erro para o Node.js

# if __name__ == "__main__":
#     conectar()

import sys
import win32com.client
import importlib
import json
import subprocess
import time
import psutil


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

# def matar_processos_sap():
#     for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
#         try:
#             nome = proc.info['name'] or ''
#             cmd = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
#             if 'sap' in nome.lower() or 'sap' in cmd.lower():
#                 print(f"Matando processo PID {proc.pid} - {nome}")
#                 proc.kill()  # mata o processo imediatamente                      
#         except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
#             return(f"Não foi possível matar processo: {e}")
    




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

        num_args = len(sys.argv)
        if num_args < 2:
            raise ValueError("Transação não foi informada!", file=sys.stderr)

        transacao = sys.argv[1].lower()
        numero_sap = sys.argv[2].lower() if num_args > 2 else None        

        modulo = importlib.import_module(f"transacoes.trans_{transacao}")
        # módulo adicional fixo, caso precise
        # modulo2 = importlib.import_module(f"transacoes.trans_clm3")
        # modulo3 = importlib.import_module(f"scripts.createZZ")

        if numero_sap:
            resultado = modulo.executar(sessoes['sessao_1'], numero_sap)
        else:
            resultado = modulo.executar(sessoes['sessao_1'])

        print(json.dumps(resultado))

    except Exception as e:
        print(f"Erro durante a execução: {e}")
        sys.exit(1)


