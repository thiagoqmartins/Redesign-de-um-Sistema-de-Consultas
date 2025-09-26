import os
import json
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize
from busca_dados_sap import dados_claim

# Caminhos
CAMINHO_MODELO = os.path.join("..", "Busca", "modelo", "paraphrase-MiniLM-L6-v2")
ARQ_DOCUMENTOS = "documentos.json"
ARQ_EMBEDDINGS = "embeddings.npy"

# Carrega modelo
tokenizer = AutoTokenizer.from_pretrained(CAMINHO_MODELO, local_files_only=True)
model = AutoModel.from_pretrained(CAMINHO_MODELO, local_files_only=True)

# Função para gerar embeddings
def gerar_embedding(texto):
    tokens = tokenizer(texto, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        output = model(**tokens)
    return output.last_hidden_state.mean(dim=1).squeeze().numpy()

# Função de busca
def buscar_documentos(consulta, documentos, embeddings_docs, top_n=5):
    embedding_consulta = normalize([gerar_embedding(consulta)])
    similaridades = cosine_similarity(embedding_consulta, embeddings_docs)[0]
    ids = list(documentos.keys())
    ordenados = sorted(enumerate(similaridades), key=lambda x: x[1], reverse=True)
    return [(ids[i], similaridades[i]) for i, _ in ordenados[:top_n]]

# Adicionar novo documento
def adicionar_documento(novo_texto, nclaim):
    if not novo_texto.strip():
        print(f"⚠️ Texto vazio para claim {nclaim}, ignorado.")
        return

    if nclaim in documentos:
        print(f"⚠️ Claim {nclaim} já existe, ignorado.")
        return

    documentos[nclaim] = novo_texto
    novo_embedding = normalize([gerar_embedding(novo_texto)])
    global embeddings_docs
    embeddings_docs = np.vstack([embeddings_docs, novo_embedding])

    with open(ARQ_DOCUMENTOS, "w", encoding="utf-8") as f:
        json.dump(documentos, f, ensure_ascii=False, indent=2)
    np.save(ARQ_EMBEDDINGS, embeddings_docs)
    print(f"✅ Documento {nclaim} adicionado.")

# Visualizar documentos
def visualizar_base():
    print("\n📄 Lista de documentos:")
    for i, (id_doc, texto) in enumerate(documentos.items()):
        print(f"{id_doc}: {texto[:80]}...")  # resumo do texto
        print(f"🔢 Embedding (resumo): {embeddings_docs[i][:5]}...\n")

# Carregar claims de arquivo
def carregar_lista_claims(caminho_arquivo):
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            return [linha.strip() for linha in f if linha.strip()]
    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {e}")
        return []

# Carregamento inicial
if os.path.exists(ARQ_DOCUMENTOS) and os.path.exists(ARQ_EMBEDDINGS):
    print("📂 Carregando dados existentes...")
    with open(ARQ_DOCUMENTOS, "r", encoding="utf-8") as f:
        documentos = json.load(f)
    embeddings_docs = np.load(ARQ_EMBEDDINGS)
else:
    print("⚙️ Gerando base inicial...")
    documentos = {}
    embeddings_docs = np.empty((0, 384))  # dimensão do MiniLM
    with open("C:\\Temp\\saida.txt", "r", encoding="latin1") as f:
        todos_documentos = json.load(f)
        for i, (doc_id, texto) in enumerate(todos_documentos.items()):
            if i >= 20:
                break
            if texto.strip():
                documentos[doc_id] = texto
                emb = gerar_embedding(texto)
                embeddings_docs = np.vstack([embeddings_docs, normalize([emb])])
    with open(ARQ_DOCUMENTOS, "w", encoding="utf-8") as f:
        json.dump(documentos, f, ensure_ascii=False, indent=2)
    np.save(ARQ_EMBEDDINGS, embeddings_docs)

# Interface principal
if __name__ == "__main__":
    print("\n🧠 Busca Semântica WEG")

    while True:
        print("\nMenu:")
        print("1 - Buscar documento")
        print("2 - Adicionar novo texto ao banco")
        print("3 - Visualizar documentos e embeddings")
        print("4 - Sair")
        print("5 - Adicionar documentos em lote (arquivo)")

        opcao = input("Escolha uma opção (1, 2, 3, 4 ou 5): ").strip()

        if opcao == "1":
            try:
                consulta = input("Digite sua busca: ").strip()
                resultados = buscar_documentos(consulta, documentos, embeddings_docs, top_n=5)
                print("\n🔍 Resultados mais semelhantes:")
                for doc_id, score in resultados:
                    print(f"{score:.2f} - {doc_id}")
            except Exception as e:
                print(f"❌ Erro na busca: {e}")

        elif opcao == "2":
            try:
                nclaim = input("Digite número da claim: ").strip()
                txt = dados_claim(nclaim)
                adicionar_documento(txt, nclaim)
            except Exception as e:
                print(f"❌ Erro ao adicionar documento: {e}")

        elif opcao == "3":
            visualizar_base()

        elif opcao == "4":
            print("👋 Encerrando o programa.")
            break

        elif opcao == "5":
            caminho = input("Digite o caminho do arquivo com os nclaims (ex: claims.txt): ").strip()
            lista_claims = carregar_lista_claims(caminho)
            for nclaim in lista_claims:
                try:
                    txt = dados_claim(nclaim)
                    adicionar_documento(txt, nclaim)
                except Exception as e:
                    print(f"⚠️ Erro ao processar {nclaim}: {e}")
        else:
            print("❌ Opção inválida.")





# import os
# import json
# import torch
# import numpy as np
# from transformers import AutoTokenizer, AutoModel
# from sklearn.metrics.pairwise import cosine_similarity
# from sklearn.preprocessing import normalize
# from busca_dados_sap import dados_claim

# # Caminhos
# CAMINHO_MODELO = os.path.join("..", "Busca", "modelo", "paraphrase-MiniLM-L6-v2")
# ARQ_DOCUMENTOS = "documentos.json"
# ARQ_EMBEDDINGS = "embeddings.npy"

# # Carrega tokenizer e modelo
# tokenizer = AutoTokenizer.from_pretrained(CAMINHO_MODELO, local_files_only=True)
# model = AutoModel.from_pretrained(CAMINHO_MODELO, local_files_only=True)

# # Função para gerar embedding de uma frase
# def gerar_embedding(texto):
#     tokens = tokenizer(texto, return_tensors="pt", truncation=True, padding=True)
#     with torch.no_grad():
#         output = model(**tokens)
#     return output.last_hidden_state.mean(dim=1).squeeze().numpy()

# # Busca semântica com IDs (mas sem incluir IDs no embedding)
# def buscar_documentos(consulta, documentos, embeddings_docs, top_n=3):
#     embedding_consulta = normalize([gerar_embedding(consulta)])
#     similaridades = cosine_similarity(embedding_consulta, embeddings_docs)[0]

#     ids = list(documentos.keys())
#     textos = list(documentos.values())
#     ordenados = sorted(enumerate(similaridades), key=lambda x: x[1], reverse=True)

#     return [(ids[i], textos[i], similaridades[i]) for i, _ in ordenados[:top_n]]

# # Adiciona novo documento ao banco
# def adicionar_documento(novo_texto, nclaim):
#     if novo_texto in documentos.values():
#         print("⚠️ Texto já existe no banco.")
#         return

#     novo_id = nclaim
#     documentos[novo_id] = novo_texto
#     novo_embedding = normalize([gerar_embedding(novo_texto)])
#     embeddings_atualizados = np.vstack([embeddings_docs, novo_embedding])

#     # Atualiza arquivos
#     with open(ARQ_DOCUMENTOS, "w", encoding="utf-8") as f:
#         json.dump(documentos, f, ensure_ascii=False, indent=2)
#     np.save(ARQ_EMBEDDINGS, embeddings_atualizados)
#     print(f"✅ Texto adicionado com sucesso. ID: {novo_id}")

# # Gera novo ID incremental
# def gerar_novo_id(documentos):
#     numeros = [int(k[2:]) for k in documentos.keys() if k.startswith("ID")]
#     proximo = max(numeros, default=0) + 1
#     return f"ID{proximo:03d}"

# # Visualiza documentos e preview de embeddings
# def visualizar_base():
#     print("\n📄 Lista de documentos:")
#     for i, (id_doc, texto) in enumerate(documentos.items()):
#         print(f"{id_doc}: {texto}")
#         print(f"🔢 Embedding {id_doc} (resumo): {embeddings_docs[i][:5]}...\n")

# if os.path.exists(ARQ_DOCUMENTOS) and os.path.exists(ARQ_EMBEDDINGS):
#     print("📂 Carregando embeddings do cache...")
#     with open(ARQ_DOCUMENTOS, "r", encoding="utf-8") as f:
#         documentos = json.load(f)
#     embeddings_docs = np.load(ARQ_EMBEDDINGS)
# else:
#     print("⚙️ Lendo arquivo e gerando embeddings iniciais...")

#     # Lê o dicionário completo do arquivo .txt
#     with open("C:\\Temp\\saida.txt", "r", encoding="latin1") as f:
#         todos_documentos = json.load(f)

#     # Seleciona apenas os 20 primeiros pares
#     documentos = dict(list(todos_documentos.items())[:20])

#     # Gera embeddings
#     embeddings_docs = normalize([gerar_embedding(texto) for texto in documentos.values()])

#     # Salva documentos e embeddings
#     with open(ARQ_DOCUMENTOS, "w", encoding="utf-8") as f:
#         json.dump(documentos, f, ensure_ascii=False, indent=2)
#     np.save(ARQ_EMBEDDINGS, embeddings_docs)


# # Execução principal
# def carregar_lista_claims(caminho_arquivo):
#     try:
#         with open(caminho_arquivo, 'r', encoding='utf-8') as f:
#             return [linha.strip() for linha in f if linha.strip()]
#     except FileNotFoundError:
#         print(f"❌ Arquivo '{caminho_arquivo}' não encontrado.")
#         return []
#     except Exception as e:
#         print(f"❌ Erro ao ler arquivo: {e}")
#         return []

# if __name__ == "__main__":
#     print("\n🧠 Busca Semântica WEG")

#     while True:
#         print("\nMenu:")
#         print("1 - Buscar documento")
#         print("2 - Adicionar novo texto ao banco")
#         print("3 - Visualizar documentos e embeddings")
#         print("4 - Sair")
#         print("5 - Adicionar documentos em lote (arquivo)")

#         opcao = input("Escolha uma opção (1, 2, 3, 4 ou 5): ").strip()

#         if opcao == "1":
#             try:
#                 consulta = input("Digite sua busca: ").strip()
#                 resultados = buscar_documentos(consulta, documentos, embeddings_docs, top_n=5)
#                 print("\n🔍 Resultados mais semelhantes:")
#                 for doc_id, texto, score in resultados:
#                     print(f"{score:.2f} - {doc_id}")
#             except Exception as e:
#                 print(f"❌ Erro na busca: {e}")

#         elif opcao == "2":
#             try:
#                 novo_texto = input("Digite número da claim: ").strip()
#                 txt_claim = dados_claim(novo_texto)
#                 adicionar_documento(txt_claim, novo_texto)
#                 print("✅ Documento adicionado.")
#             except Exception as e:
#                 print(f"❌ Erro ao adicionar documento: {e}")

#         elif opcao == "3":
#             try:
#                 visualizar_base()
#             except Exception as e:
#                 print(f"❌ Erro ao visualizar base: {e}")

#         elif opcao == "4":
#             print("👋 Encerrando o programa.")
#             break

#         elif opcao == "5":
#             caminho = input("Digite o caminho do arquivo com os nclaims (ex: claims.txt): ").strip()
#             lista_claims = carregar_lista_claims(caminho)

#             if not lista_claims:
#                 print("⚠️ Nenhum claim encontrado no arquivo.")
#             else:
#                 print(f"🔁 Processando {len(lista_claims)} claims...\n")
#                 for nclaim in lista_claims:
#                     try:
#                         txt_claim = dados_claim(nclaim)
#                         adicionar_documento(txt_claim, nclaim)
#                         print(f"✅ Claim {nclaim} adicionada.")
#                     except Exception as e:
#                         print(f"⚠️ Erro ao processar {nclaim}: {e}")

#         else:
#             print("❌ Opção inválida. Tente novamente.")


# #  Carregamento inicial
# # if os.path.exists(ARQ_DOCUMENTOS) and os.path.exists(ARQ_EMBEDDINGS):
# #     print("📂 Carregando embeddings do cache...")
# #     with open(ARQ_DOCUMENTOS, "r", encoding="utf-8") as f:
# #         documentos = json.load(f)
# #     embeddings_docs = np.load(ARQ_EMBEDDINGS)
# # else:
# #     documentos = {

# #     }        

# #     embeddings_docs = normalize([gerar_embedding(texto) for texto in documentos.values()])
# #     with open(ARQ_DOCUMENTOS, "w", encoding="utf-8") as f:
# #         json.dump(documentos, f, ensure_ascii=False, indent=2)
# #     np.save(ARQ_EMBEDDINGS, embeddings_docs)
