import matplotlib.pyplot as plt
import numpy as np

# Função do 1º grau: f(x) = 2x + 3
x1 = np.linspace(-10, 10, 400)
y1 = 2 * x1 + 3

# Função do 2º grau: f(x) = x^2 - 4x + 3
x2 = np.linspace(-2, 6, 400)
y2 = x2**2 - 4 * x2 + 3

# Criar os gráficos lado a lado
fig, axs = plt.subplots(1, 2, figsize=(12, 5))

# Gráfico da função do 1º grau
axs[0].plot(x1, y1, color='blue', label='f(x) = 2x + 3')
axs[0].axhline(0, color='black', linewidth=0.5)
axs[0].axvline(0, color='black', linewidth=0.5)
axs[0].set_title('Função do 1º Grau')
axs[0].set_xlabel('x')
axs[0].set_ylabel('f(x)')
axs[0].legend()
axs[0].grid(True)

# Gráfico da função do 2º grau
axs[1].plot(x2, y2, color='green', label='f(x) = x² - 4x + 3')
axs[1].axhline(0, color='black', linewidth=0.5)
axs[1].axvline(0, color='black', linewidth=0.5)
axs[1].set_title('Função do 2º Grau')
axs[1].set_xlabel('x')
axs[1].set_ylabel('f(x)')
axs[1].legend()
axs[1].grid(True)

plt.tight_layout()
plt.show()
