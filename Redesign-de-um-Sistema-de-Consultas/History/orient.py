
class Animal():
    def falar(self):
        print("O animal faz algum som.")
    def Teste(self):
        print("Teste")    

class Cachorro(Animal):
    def falar(self):
        print("O cachorro late: Au au!")
    def Teste(self):
        """
        Prints the string "Teste" to the console.

        This method serves as a simple demonstration of a print statement.
        """
        print("Teste")


class Gato(Animal):
    def falar(self):
        print("O gato mia: Miau!")
    def Teste(self):
        print("Teste")

# Função que aceita qualquer animal
def fazer_animal_falar(animal):
    animal.falar()
    animal.Teste()

# Criando os objetos
animal1 = Cachorro()
animal2 = Gato()
animal3 = Animal()

# Chamando a função para cada um
fazer_animal_falar(animal1)
fazer_animal_falar(animal2)
fazer_animal_falar(animal3)

