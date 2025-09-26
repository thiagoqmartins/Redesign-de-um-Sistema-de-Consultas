import json
import pandas as pd
import re

# Caminho para o arquivo JSON
caminho_arquivo = r"C:\Users\thiagoqm\Desktop\VBA_Prog\Python\projeto1\busca\documentos.json"

# Função para remover caracteres inválidos para o Excel
def limpar_texto(texto):
    if not isinstance(texto, str):
        return texto
    return re.sub(r"[\x00-\x1F\x7F]", "", texto)

# 1. Carrega o JSON
with open(caminho_arquivo, "r", encoding="utf-8") as f:
    dados = json.load(f)

# 2. Limpa os textos
dados_limpos = {k: limpar_texto(v) for k, v in dados.items()}

# 3. Converte para DataFrame
df = pd.DataFrame(list(dados_limpos.items()), columns=["Número", "Texto"])

# 4. Salva como planilha Excel
df.to_excel("saida.xlsx", index=False)

print("✅ Planilha criada com sucesso: saida.xlsx")
