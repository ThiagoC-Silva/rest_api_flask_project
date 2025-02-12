# Imagem base do Docker
FROM python:3.13.1-slim-bookworm 
# Porta padrão do Flask para conexões externas
EXPOSE 5000
# Diretório de trabalho dentro do container]
WORKDIR /app
# Instala as dependências do projeto
COPY requirements.txt . 
# RUN pip install -r requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt
#  Copia os arquivos do diretório atual para o diretório de trabalho
COPY . .
# Comando padrão ao iniciar o container
# CMD ["flask", "run", "--host", "0.0.0.0"]
CMD ["gunicorn", "--bind", "0.0.0.0:80", "app:create_app()"]


# Comando para rodar container
# 1. docker run -dp 500:500 -w /app -v "$(pwd):/app" <image_name> sh -c "flask run --host 0.0.0.0"
# 2. docker run -dp 5000:5000 -w /app -v "$(PWD):/app" --name <container_name> image_name
