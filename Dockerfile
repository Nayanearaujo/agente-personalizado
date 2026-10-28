# Imagem do serviço, em dois estágios. Roda igual no computador, no Hugging Face
# (Space tipo Docker) e no Railway: a aplicação não pertence à plataforma.

# ---------- Estágio 1: compila a interface React ----------
FROM node:24-slim AS interface
WORKDIR /frontend
COPY frontend/package.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build        # gera /frontend/dist

# ---------- Estágio 2: o servidor Python ----------
FROM python:3.12-slim

# Usuário sem privilégios (não roda como root).
RUN useradd --create-home assistente
WORKDIR /app

# Só as bibliotecas do servidor (sem pymupdf4llm, que é da indexação).
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Baixa o modelo de embedding para dentro da imagem, para o serviço subir
# rápido e sem depender do Hugging Face em tempo de execução.
RUN python -c "from fastembed import TextEmbedding; TextEmbedding(model_name='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')"

# O código e os arquivos que o servidor usa.
COPY agente/ ./agente/
COPY config.yaml ./
COPY assets/ ./assets/
COPY --from=interface /frontend/dist ./frontend/dist

USER assistente
# O Railway e o HF informam a porta na variável PORT (padrão 7860).
ENV PORT=7860
EXPOSE 7860
CMD ["sh", "-c", "uvicorn agente.servidor:app --host 0.0.0.0 --port ${PORT:-7860}"]
