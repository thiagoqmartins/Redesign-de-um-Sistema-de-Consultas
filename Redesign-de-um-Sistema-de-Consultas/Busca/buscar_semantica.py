# from transformers import AutoTokenizer, AutoModel
# import torch

# modelo_path = './modelo/paraphrase-MiniLM-L6-v2'

# tokenizer = AutoTokenizer.from_pretrained(modelo_path)
# model = AutoModel.from_pretrained(modelo_path)

# # Exemplo de uso
# frase = "Exemplo de frase"
# tokens = tokenizer(frase, return_tensors='pt')
# with torch.no_grad():
#     embeddings = model(**tokens).last_hidden_state.mean(dim=1)

# print(embeddings)

import os
import torch
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity

# Caminho do modelo salvo localmente
CAMINHO_MODELO = os.path.join("..", "Busca", "modelo", "paraphrase-MiniLM-L6-v2")

# Carrega modelo e tokenizer localmente
tokenizer = AutoTokenizer.from_pretrained(CAMINHO_MODELO, local_files_only=True)
model = AutoModel.from_pretrained(CAMINHO_MODELO, local_files_only=True)

# Função para gerar embedding médio
def gerar_embedding(texto):
    tokens = tokenizer(texto, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        output = model(**tokens)
    return output.last_hidden_state.mean(dim=1).squeeze().numpy()

# Exemplos de documentos para comparar
documentos = [
    "A WEG apresentou sua nova linha de redutores industriais.",
    "A turbina eólica da WEG alcançou eficiência recorde em testes de campo.",
    "Redutores planetários são ideais para aplicações de alto torque.",
    "A manutenção preventiva dos redutores aumenta a vida útil do equipamento.",
    "A nova turbina da WEG foi projetada para operar com menor nível de ruído.",
    "Motores WEG são compatíveis com redutores helicoidais de última geração.",
    "Os redutores WEG oferecem alto desempenho mesmo em ambientes agressivos.",
    "A integração dos redutores com sistemas IoT permite monitoramento remoto.",
    "WEG desenvolveu uma turbina hidráulica voltada para pequenas centrais elétricas.",
    "O sistema de ventilação da nova turbina da WEG garante refrigeração eficiente.",
    "Redutores cônicos da WEG são usados em transportadores industriais pesados.",
    "A linha WCG20 de redutores foi otimizada para reduzir perdas por atrito.",
    "A turbina eólica G132 foi instalada no parque de geração renovável do sul do país.",
    "Clientes da WEG destacam a confiabilidade dos redutores em operações contínuas.",
]

# Gera embedding dos documentos
embeddings_docs = [gerar_embedding(doc) for doc in documentos]

# Entrada do usuário
consulta = input("Digite sua busca: ")
embedding_consulta = gerar_embedding(consulta).reshape(1, -1)

# Similaridade
similaridades = cosine_similarity(embedding_consulta, embeddings_docs)[0]
ordenados = sorted(enumerate(similaridades), key=lambda x: x[1], reverse=True)

# Mostra resultados
print("\n🔍 Resultados mais semelhantes:")
for idx, score in ordenados:
    print(f"{score:.2f} - {documentos[idx]}")
