# Imagem base do Docker
FROM python:3.13.1-slim-bookworm 
# Porta padrão do Flask para conexões externas
EXPOSE 5000
# Diretório de trabalho dentro do container]
WORKDIR /app
# Instala as dependências do projeto
COPY requirements.txt . 
RUN pip install -r requirements.txt
#  Copia os arquivos do diretório atual para o diretório de trabalho
COPY . .
# Comando padrão ao iniciar o container
CMD ["flask", "run", "--host", "0.0.0.0"]