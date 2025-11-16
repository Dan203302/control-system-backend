FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app
COPY api-gateway/requirements.txt ./api-gateway/requirements.txt
RUN pip install --no-cache-dir -r api-gateway/requirements.txt
COPY common/ ./common/
COPY api-gateway/ ./api-gateway/
WORKDIR /app/api-gateway
ENV PORT=8080
EXPOSE 8080
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
