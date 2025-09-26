from transformers import AutoTokenizer, AutoModel
import os


os.environ["HF_HUB_DISABLE_SSL_VERIFICATION"] = "1"

modelo_id = "sentence-transformers/paraphrase-MiniLM-L6-v2"
pasta_destino = "./modelo_salvo"

# Baixa e salva o modelo e o tokenizer
tokenizer = AutoTokenizer.from_pretrained(modelo_id)
model = AutoModel.from_pretrained(modelo_id)

tokenizer.save_pretrained(pasta_destino)
model.save_pretrained(pasta_destino)

print(f"Modelo salvo em: {os.path.abspath(pasta_destino)}")
