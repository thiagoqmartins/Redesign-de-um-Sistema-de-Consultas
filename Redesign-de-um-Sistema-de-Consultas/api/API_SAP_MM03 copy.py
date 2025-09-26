import requests
import datetime

# Data atual
hoje = datetime.datetime.now()


# Função para buscar o valor da indicação do item material
def get_nested_value_Recursevely(nested_dict, value_to_find):
    if isinstance(nested_dict, dict):
        for key, value in nested_dict.items():
            if value == value_to_find:
                return nested_dict
            result = get_nested_value_Recursevely(value, value_to_find)
            if result is not None:
                return result
    elif isinstance(nested_dict, list):
        for item in nested_dict:
            result = get_nested_value_Recursevely(item, value_to_find)
            if result is not None:
                return result

# Obtendo informações do usuário
material = input("Digite o número do material: ")


# Constrói a URL e o payload
url = "https://wdt-cache.weg.net"
route = "material_eem"
model = {
    "Material": {
        "language": "pt",
        "LoadValueDesc": 'false',
        "ValidFrom": f"{hoje:%Y-%m-%d}",
        "ReturnClassification": 'true',
        "ReturnVariantEvaluation": 'true',
        "SearchBy": {
            "Material": {
                "MaterialList": {
                    "Material": {
                        "MaterialNumber": material
                    }
                }
            }
        }
    }
}
headers = {
    "Accept": "application/json",
    "User-Agent": "shaft-tests",
    "Content-Type": "application/json"
}

# Faz a requisição POST
try:
    resp = requests.post(f"{url}/{route}", json=model, headers=headers).json()
    print(resp)
except Exception as e:
    print(f"Erro ao buscar informações: {e}")


print("Programa concluído!")