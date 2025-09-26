import sys
import win32com.client
import importlib
import json
from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)  # Cria o objeto app

@app.route('/api/dados')
def obter_dados():
    
    try:
        conn = sqlite3.connect('BD/banco_dados.db')
        cursor = conn.cursor()

        cursor.execute('''
            SELECT 
                tipo_nota, numero_nota, numero_ordem, cliente, nome_lista, descricao,
                texto_medida, inicio_desejado, fim_planejado, fim_desejado, status,
                data_criacao, criado_por, notificador
            FROM consultas_iqs9
            WHERE nome_lista = ?
        ''')

        linhas = cursor.fetchall()
        colunas = [desc[0] for desc in cursor.description]
        resultado = [dict(zip(colunas, linha)) for linha in linhas]

        conn.close()
        return jsonify(resultado)
    except Exception as e:
        print('Erro no servidor:', e)
        return jsonify({'error': 'Erro interno no servidor'}), 500

if __name__ == '__main__':
    app.run(debug=True)