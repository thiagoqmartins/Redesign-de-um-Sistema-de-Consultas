import win32com.client
import ctypes

try:
    
    print("Tentando conectar ao SAP GUI...")
    
    SapGuiAuto = win32com.client.GetObject("SAPGUI")
    if not SapGuiAuto:
        raise Exception("SAP GUI não encontrado. Verifique se está aberto!")
    
    application = SapGuiAuto.GetScriptingEngine
    if not application:
        raise Exception("Não foi possível obter o Scripting Engine.")

    connection = application.Children(0)
    if not connection:
        raise Exception("Nenhuma conexão encontrada. Você está logado no SAP?")

    session = connection.Children(0)
    if not session:
        raise Exception("Nenhuma sessão ativa encontrada.")
   
    session.findById("wnd[0]/tbar[0]/okcd").text = "/nmm03"
    session.findById("wnd[0]").sendVKey(0)  # Pressiona Enter
    session.findById("wnd[0]/usr/ctxtRMMG1-MATNR").text = "18006381"
    session.findById("wnd[0]").sendVKey(0)

    print("Conexão com SAP estabelecida!")
    
except Exception as e:
    print(f"Erro ao conectar ao SAP: {e}")
