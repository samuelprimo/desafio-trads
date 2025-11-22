FROM python:3.11-slim

WORKDIR /app

#instala dependências do sistema para o Postgres
RUN apt-get update && apt-get install -y libpq-dev gcc

#copia o requirements da raiz para dentro da pasta backend no container
COPY requirements.txt . 

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

#roda com uvicorn na porta 5000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]