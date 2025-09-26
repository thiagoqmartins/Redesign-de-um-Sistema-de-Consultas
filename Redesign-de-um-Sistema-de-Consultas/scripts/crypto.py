import bcrypt # ❌ externo — instalar com: pip install bcrypt
import sys

def crypto(a):
    # Gerar um salt e hashear a senha
    salt = bcrypt.gensalt()
    senha_hash = bcrypt.hashpw(a.encode('utf-8'), salt)

    # Retorna o hash
    return senha_hash.decode()

def verificar_senha(senha, hash_salvo):
    try:
        a = bcrypt.checkpw(senha.encode('utf-8'), hash_salvo.encode('utf-8'))
        return a
    except Exception as e:
        print(f"Erro: {str(e)}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 1:  
        sys.exit(1)

    senha = sys.argv[1]
    resultado = crypto(senha)
    print(resultado)
    
else:       
    senha = (sys.argv[1]+1)
    hash_passado = sys.argv[2]
    resultado = verificar_senha(senha, hash_passado)
    print(resultado)
