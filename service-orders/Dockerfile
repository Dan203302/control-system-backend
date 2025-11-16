FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app
COPY service-orders/requirements.txt ./service-orders/requirements.txt
RUN pip install --no-cache-dir -r service-orders/requirements.txt
COPY common/ ./common/
COPY service-orders/ ./service-orders/
WORKDIR /app/service-orders
ENV PORT=8002
EXPOSE 8002
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
