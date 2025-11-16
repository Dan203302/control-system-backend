FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app
COPY service-users/requirements.txt ./service-users/requirements.txt
RUN pip install --no-cache-dir -r service-users/requirements.txt
COPY common/ ./common/
COPY service-users/ ./service-users/
WORKDIR /app/service-users
ENV PORT=8001
EXPOSE 8001
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
