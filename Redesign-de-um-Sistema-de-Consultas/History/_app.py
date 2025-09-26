from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

@app.route('/executar', methods=['POST'])
def executar():
    try:
        # exe_path = r"C:\Project1.exe"
        exe_path =r"C:\Users\thiagoqm\Desktop\Gestão de Solicitações (CLAIM).exe"

        if not os.path.exists(exe_path):
            return jsonify({'mensagem': f'Executável não encontrado em {exe_path}'}), 404

        # Executa e espera o programa terminar
        resultado = subprocess.run([exe_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Exibe a saída no terminal para debug
        print("Saída padrão:", resultado.stdout)
        print("Erro padrão:", resultado.stderr)

        # Verifica se o programa rodou corretamente
        if resultado.returncode == 0:
            return jsonify({'mensagem': 'Programa executado e finalizado com sucesso!'})
        else:
            return jsonify({'mensagem': f'Erro ao executar: {resultado.stderr}'}), 500

    except Exception as e:
        print(f"Erro no servidor: {str(e)}")  # Debug no terminal
        return jsonify({'mensagem': f'Ocorreu um erro no servidor: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
