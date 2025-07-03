FROM python:3.11-slim

# Atualize pacotes e instale dependências de sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
  gcc \
  g++ \
  make \
  ffmpeg \
  libsm6 \
  libxext6 \
  libgl1 \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
  ENVIRONMENT=production

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código da aplicação
COPY . .

# Expor porta da aplicação
EXPOSE 8080

# Comando de inicialização
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
