import numpy as np
import pandas as pd
from plotnine import ggplot, aes, geom_point, geom_abline
from PIL import Image 
from pathlib import Path # Importa para lidar com caminhos

# 1. Carregar os dados
# Descobre o diretório do script e constrói o caminho para os arquivos x.txt e y.txt
try:
    # Obtém o diretório do script
    diretorio_script = Path(__file__).resolve().parent
    
    # Constrói o caminho completo para os arquivos
    caminho_x = diretorio_script / "x.txt"
    caminho_y = diretorio_script / "y.txt"

    # Carrega os dados usando o caminho absoluto
    X = np.loadtxt(caminho_x)
    y = np.loadtxt(caminho_y)
    
except NameError:
    # Usa a abordagem de caminho relativo como fallback, que é a original.
    X = np.loadtxt("x.txt")
    y = np.loadtxt("y.txt")

# Garante que X seja uma matriz coluna
X = X.reshape(-1, 1)

# 2. Adicionar coluna de 1s para o intercepto
X_b = np.hstack([np.ones((X.shape[0], 1)), X])

# 3. Fórmula matricial da regressão linear
beta = np.linalg.inv(X_b.T @ X_b) @ X_b.T @ y

a = beta[0] # intercepto
b = beta[1] # coeficiente angular

print(f"Intercepto (a): {a}")
print(f"Slope (b): {b}")

# 4. Gerar gráfico
df = pd.DataFrame({"x": X.flatten(), "y": y})

plot = (
  ggplot(df, aes("x", "y"))
  + geom_point()
  + geom_abline(intercept=a, slope=b)
)

# 5. Salvar gráfico
plot.save("grafico.png")

# 6. Abre o gráfico automaticamente
img = Image.open("grafico.png")
img.show()