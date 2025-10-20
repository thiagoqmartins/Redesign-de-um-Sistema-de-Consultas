import json

def palavraChave():
    return ['"WEG"', '"SIEMENS"', '"SEW"', '"METSO"', '"PETROBRAS"', '"SULCROALCOOLEIRO"', '"PAPEL E CELULOSE"',  '"MINERAÇÃO"']
    # return [""]

if __name__ == "__main__":
    print(json.dumps(palavraChave()))  
