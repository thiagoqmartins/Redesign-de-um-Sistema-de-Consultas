from flask import Flask, request, jsonify
from flask_cors import CORS  
import win32com.client
import ctypes  # Biblioteca para criar MessageBox no Windows

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Habilita CORS para aceitar requisições de qualquer origem

@app.route('/executar', methods=['POST'])
def executar():
    try:
       
        print("🔍 Tentando conectar ao SAP GUI...")
        SapGuiAuto = win32com.client.GetObject("SAPGUI")       
        print("✅ SAP GUI encontrado!")

        if not SapGuiAuto:
            raise Exception("SAP GUI não está aberto.")

        application = SapGuiAuto.GetScriptingEngine
        print("✅ Scripting Engine carregado!")

        if application.Children.Count == 0:
            raise Exception("Nenhuma conexão ativa encontrada no SAP.")

        connection = application.Children(0)  # Seleciona a primeira conexão ativa
        print("✅ Conexão com SAP estabelecida!")

        if connection.Children.Count == 0:
            raise Exception("Nenhuma sessão ativa encontrada no SAP.")

        session = connection.Children(0)  # Seleciona a primeira sessão
        print("✅ Sessão SAP obtida!")

        print("🔍 Enviando comandos para o SAP...")
        session.findById("wnd[0]/tbar[0]/okcd").text = "/nmm03"
        session.findById("wnd[0]").sendVKey(0)  # Envia Enter para carregar a transação
        session.findById("wnd[0]/usr/ctxtRMMG1-MATNR").text = "12345678"
        session.findById("wnd[0]").sendVKey(0)  # Envia Enter para acessar os dados

        print("✅ Comandos enviados com sucesso!")

        return jsonify({'mensagem': 'SAP conectado e comandos executados com sucesso!'}), 200

    except Exception as e:
        print(f"❌ Erro no servidor: {str(e)}")  # Exibe o erro no terminal
        return jsonify({'mensagem': f'Erro ao executar: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)

            
        
# # def entrar_dados_basicos(self, session):
# def executary(session):
#         try:
#             # Usando "/n" para garantir que o SAP "limpe" a tela atual e vá para a transação MM03
#             session.findById("wnd[0]/tbar[0]/okcd").text = "/nmm03"
#             session.findById("wnd[0]").sendVKey(0)  # Envia Enter para carregar a transação
#             session.findById("wnd[0]/usr/ctxtRMMG1-MATNR").text = "12345678"
#             session.findById("wnd[0]").sendVKey(0)  # Envia Enter para acessar os dados
#         except Exception as e:
#             raise Exception("Erro ao entrar na transação MM03 para Dados Básicos: " + str(e))
        
# def executarx():
#     try:
#         exe_path = r"Q:\PUBLIC\WEN_TGM_SOLUCOES_TECNOLOGICAS\Gestão de Solicitações (CLAIM) v3.4.exe"

#         if not os.path.exists(exe_path):
#             return jsonify({'mensagem': f'Executável não encontrado em {exe_path}'}), 404

#         # Executa e espera o programa terminar
#         resultado = subprocess.run([exe_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

#         # Exibe a saída no terminal para debug
#         print("Saída padrão:", resultado.stdout)
#         print("Erro padrão:", resultado.stderr)

#         if resultado.returncode == 0:
#             return jsonify({'mensagem': 'Programa executado e finalizado com sucesso!'})
#         else:
#             return jsonify({'mensagem': f'Erro ao executar: {resultado.stderr}'}), 500

#     except Exception as e:
#         print(f"Erro no servidor: {str(e)}")  # Debug no terminal
#         return jsonify({'mensagem': f'Ocorreu um erro no servidor: {str(e)}'}), 500

# if __name__ == '__main__':
#     app.run(debug=True)
#     # app.run(host="0.0.0.0", port=5000, debug=True)

